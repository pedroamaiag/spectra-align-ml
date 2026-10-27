// AREA DE ESTUDO
var states = ee.FeatureCollection('IBGE/UF/V2025');

var ceara = states
    .filter(ee.Filter.eq('SIGLA_UF', 'CE'))
    .geometry();


// GRADE DE 5 KM
var grid_size = 5000;

var projection = ee.Projection('EPSG:32724');

var grid = ceara.coveringGrid({
    proj: projection,
    scale: grid_size
});


// SETORES DE 35 KM
var sector_size = 35000;

var sectors = ceara.coveringGrid({
    proj: projection,
    scale: sector_size
});


// ADICIONA NUMERO ALEATORIO FIXO A GRADE
var randomized_grid = grid.randomColumn('random', 42);


// ESCOLHE UM QUADRADO DE 5 KM POR SETOR
var distributed_regions = sectors.map(function (sector) {
    var candidates = randomized_grid
        .filterBounds(sector.geometry())
        .sort('random');

    return ee.Feature(candidates.first());
});


// REMOVE POSSIVEIS REPETICOES
distributed_regions = distributed_regions.distinct('system:index');


// SELECIONA 100 REGIOES
var selected_regions = distributed_regions
    .randomColumn('selection', 42)
    .sort('selection')
    .limit(100);


// VISUALIZACAO
Map.centerObject(ceara, 7);

// Ceara somente com contorno vermelho
var ceara_style = ee.FeatureCollection([
    ee.Feature(ceara)
]).style({
    color: 'red',
    fillColor: '00000000',
    width: 2
});

Map.addLayer(
    ceara_style,
    {},
    'Ceara'
);


// Regioes selecionadas em amarelo
var regions_style = selected_regions.style({
    color: 'yellow',
    fillColor: 'FFFF0040',
    width: 3
});

Map.addLayer(
    regions_style,
    {},
    '100 regioes'
);


// INFORMACOES
print('Quadrados de 5 km:', grid.size());
print('Setores de 35 km:', sectors.size());
print('Regioes distribuidas:', distributed_regions.size());
print('Regioes selecionadas:', selected_regions.size());