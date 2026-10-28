// MODULOS
var regions = require(
    'users/pedroamaiag/spectra-align-ml:modules/regions'
);

var sentinel = require(
    'users/pedroamaiag/spectra-align-ml:modules/sentinel'
);


// REGIOES
var selected_regions = regions.select_regions(100);
var study_area = selected_regions.geometry();


// PERIODO
var start_date = '2025-01-01';
var end_date = '2026-01-01';


// SENTINEL-2
var l1c = sentinel.get_l1c(
    study_area, start_date, end_date
);

var l2a = sentinel.get_l2a(
    study_area, start_date, end_date
);


// ENCONTRA PARES
var pairs = sentinel.find_pairs(l1c, l2a);


// INFORMACOES
print('Regioes selecionadas:', selected_regions.size());
print('Imagens L1C encontradas:', l1c.size());
print('Imagens L2A encontradas:', l2a.size());
print('Pares L1C + L2A:', pairs.size());

print(
    'IDs dos primeiros pares:',
    pairs.aggregate_array('system:index').slice(0, 10)
);
