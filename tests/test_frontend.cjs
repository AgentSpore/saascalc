const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../static/index.html'), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const calculators = {
  ltv: ['calcLTV', 'res-ltv'], cac: ['calcCAC', 'res-cac'],
  mrr: ['calcMRR', 'res-mrr'], runway: ['calcRunway', 'res-runway'],
  payback: ['calcPayback', 'res-payback'], churn: ['calcChurn', 'res-churn'],
  qr: ['calcQuickRatio', 'res-quick-ratio'], ndr: ['calcNDR', 'res-ndr'],
  r40: ['calcRule40', 'res-rule-of-40'], all: ['calcAll', 'res-all'],
  cmp: ['calcCompare', 'res-compare'],
};

function element(attributes = {}, label = '') {
  return {
    value: attributes.value || '', innerHTML: '', textContent: '', children: [], style: {},
    classList: { add() {}, remove() {} },
    getAttribute: name => attributes[name] ?? null,
    setAttribute(name, value) { attributes[name] = value; },
    removeAttribute(name) { delete attributes[name]; },
    closest: () => ({ querySelector: () => ({ textContent: label }) }),
    replaceChildren(...children) { this.children = children; this.innerHTML = ''; },
    appendChild(child) { this.children.push(child); },
    focus() {},
  };
}

function fixture(response = {}) {
  const elements = {};
  for (const match of html.matchAll(/<label>(.*?)<\/label><input ([^>]+)>/g)) {
    const attributes = Object.fromEntries([...match[2].matchAll(/([\w-]+)="([^"]*)"/g)].map(m => [m[1], m[2]]));
    elements[attributes.id] = element(attributes, match[1]);
  }
  for (const [, result] of Object.values(calculators)) elements[result] = element();
  const calls = [];
  const context = vm.createContext({
    window: { location: { origin: 'http://localhost' } },
    document: {
      getElementById: id => elements[id], querySelectorAll: () => [],
      createElement: () => element(),
    },
    fetch: async (url, options) => {
      calls.push({ url, body: JSON.parse(options.body) });
      return { ok: response.ok ?? true, statusText: 'Unprocessable Entity', json: async () => response.body ?? {} };
    },
  });
  vm.runInContext(script, context);
  return { elements, calls, context };
}

function resultText(result) {
  return result.textContent + result.innerHTML + result.children.map(child => child.textContent).join('');
}

for (const match of html.matchAll(/<input type="number" id="([^"]+)"/g)) {
  const id = match[1];
  for (const invalid of ['', 'Infinity', 'not-a-number']) {
    test(`${id} rejects ${JSON.stringify(invalid)} before HTTP`, async () => {
      const f = fixture();
      f.elements[id].value = invalid;
      const [calculate, result] = calculators[id.split('-')[0]];
      await f.context[calculate]();
      assert.equal(f.calls.length, 0);
      assert.match(resultText(f.elements[result]), /enter|required|finite|number/i);
      assert.equal(f.elements[id].getAttribute('aria-invalid'), 'true');
    });
  }
}

for (const id of ['mrr-customers', 'cac-acquired', 'churn-start', 'churn-lost', 'churn-period', 'all-acquired', 'cmp-a-acquired', 'cmp-b-acquired']) {
  test(`${id} rejects fractional customers or days`, async () => {
    const f = fixture();
    f.elements[id].value = '1.5';
    const [calculate, result] = calculators[id.split('-')[0]];
    await f.context[calculate]();
    assert.equal(f.calls.length, 0);
    assert.match(resultText(f.elements[result]), /whole|integer/i);
  });
}

test('MRR preserves valid zeros and decimal ARPU', async () => {
  const f = fixture({ body: { mrr: 0, arr: 0 } });
  f.elements['mrr-customers'].value = '0';
  f.elements['mrr-arpu'].value = '0';
  await f.context.calcMRR();
  assert.deepEqual(f.calls[0].body, { customers: 0, arpu: 0 });
  f.elements['mrr-customers'].value = '100';
  f.elements['mrr-arpu'].value = '50.25';
  await f.context.calcMRR();
  assert.deepEqual(f.calls[1].body, { customers: 100, arpu: 50.25 });
  assert.equal(f.elements['mrr-customers'].getAttribute('aria-invalid'), null);
});

for (const [id, value] of [['ltv-churn', '101'], ['payback-margin', '0'], ['all-arpu', '0'], ['cmp-b-churn', '0'], ['qr-new', '-1'], ['ndr-start', '0'], ['runway-cash', '-1']]) {
  test(`${id} rejects out-of-range ${value}`, async () => {
    const f = fixture();
    f.elements[id].value = value;
    await f.context[calculators[id.split('-')[0]][0]]();
    assert.equal(f.calls.length, 0);
  });
}

test('Rule of 40 permits negative growth and profit', async () => {
  const f = fixture({ body: {} });
  f.elements['r40-growth'].value = '-20';
  f.elements['r40-profit'].value = '-10';
  await f.context.calcRule40();
  assert.deepEqual(f.calls[0].body, { revenue_growth_rate_pct: -20, profit_margin_pct: -10 });
});

test('API validation array shows field and readable message as text', async () => {
  const message = '<img src=x onerror=alert(1)> must be valid';
  const f = fixture({ ok: false, body: { detail: [{ loc: ['body', 'customers'], msg: message }] } });
  await f.context.calcMRR();
  const result = f.elements['res-mrr'];
  assert.match(resultText(result), /customers:.*must be valid/);
  assert.doesNotMatch(resultText(result), /\[object Object\]/);
  assert.equal(result.innerHTML, '');
  assert.equal(result.children[0].textContent, `customers: ${message}`);
});

for (const [value, expected] of [[0, '0 mo'], [null, 'N/A']]) {
  test(`dashboard preserves ${value} runway/payback`, async () => {
    const f = fixture({ body: { runway: { runway_months: value }, payback: { payback_months: value }, ltv_cac_ratio: { ratio: value } } });
    await f.context.calcAll();
    const result = f.elements['res-all'].innerHTML;
    assert.match(result, new RegExp(`Runway</div><div[^>]+>${expected}`));
    assert.match(result, new RegExp(`Payback</div><div[^>]+>${expected}`));
    assert.match(result, new RegExp(`LTV/CAC</div><div[^>]+>${value === 0 ? '0x' : 'N/A'}`));
  });
}

test('comparison renders both user-provided labels as literal text', async () => {
  const labelA = '<img src=x onerror=alert(1)>';
  const labelB = '<svg onload=alert(2)> & "B"';
  assert.ok(labelA.length <= 50 && labelB.length <= 50);
  const f = fixture({ body: { labels: { a: labelA, b: labelB }, metrics: {} } });
  f.elements['cmp-a-label'].value = labelA;
  f.elements['cmp-b-label'].value = labelB;
  await f.context.calcCompare();
  assert.equal(f.calls[0].body.period_a_label, labelA);
  assert.equal(f.calls[0].body.period_b_label, labelB);
  const result = f.elements['res-compare'].innerHTML;
  assert.doesNotMatch(result, /<img|<svg/);
  assert.equal(result, '<h3>&lt;img src=x onerror=alert(1)&gt; vs &lt;svg onload=alert(2)&gt; &amp; &quot;B&quot;</h3>');
});

test('API validation without field location has no leading separator', async () => {
  const f = fixture({ ok: false, body: { detail: [{ loc: ['body'], msg: 'Value error, customers lost exceeds customers at start' }] } });
  await f.context.calcMRR();
  assert.equal(f.elements['res-mrr'].children[0].textContent, 'Value error, customers lost exceeds customers at start');
});
