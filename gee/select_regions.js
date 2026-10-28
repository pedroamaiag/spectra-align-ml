// IMPORTA O MODULO
var regions = require('users/SEU_USUARIO/SEU_REPOSITORIO:modules/regions');


// SELECIONA REGIOES
var ceara = regions.get_ceara();
var selected_regions = regions.select_regions(100);


// VISUALIZACAO
Map.centerObject(ceara, 7);

var ceara_style = ee.FeatureCollection([
    ee.Feature(ceara)
]).style({
    color: 'red',
    fillColor: '00000000',
    width: 2
});

Map.addLayer(ceara_style, {}, 'Ceara');

var regions_style = selected_regions.style({
    color: 'yellow',
    fillColor: 'FFFF0040',
    width: 3
});

Map.addLayer(regions_style, {}, '100 regioes');


// INFORMACOES
print('Regioes selecionadas:', selected_regions.size());

print(
    'Primeira regiao:',
    ee.Feature(selected_regions.first()).get('system:index')
);