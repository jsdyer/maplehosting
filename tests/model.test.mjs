import test from 'node:test';import assert from 'node:assert/strict';
import {analyse} from '../web/model.mjs';
test('network shares count a domain once per network, not once per address',()=>{const a=analyse([{networks:['A','A','B'],countries:['CA'],country_group:'Canada only',ipv6:'Yes'}]);assert.equal(a.panels[1].items.find(r=>r.label==='A').value,1);assert.equal(a.metrics[0].value,1);});
