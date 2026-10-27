// AREA DE ESTUDO
var states = ee.FeatureCollection('IBGE/UF/V2025');

var ceara = states
    .filter(ee.Filter.eq('SIGLA_UF', 'CE'))
    .geometry();


// GRADE DE 5 KM
var projection = ee.Projection('EPSG:32724');

var grid = ceara.coveringGrid({
    proj: projection,
    scale: 5000
});


// SETORES DE 35 KM
var sectors = ceara.coveringGrid({
    proj: projection,
    scale: 35000
});


// DISTRIBUI AS REGIOES
var randomized_grid = grid.randomColumn('random', 42);

var distributed_regions = sectors.map(function (sector) {
    var candidates = randomized_grid
        .filterBounds(sector.geometry())
        .sort('random');

    return ee.Algorithms.If(
        candidates.size().gt(0),
        candidates.first(),
        null
    );
}, true);

distributed_regions = distributed_regions.distinct('system:index');


// SELECIONA 100 REGIOES
var selected_regions = distributed_regions
    .randomColumn('selection', 42)
    .sort('selection')
    .limit(100);


// PERIODO
var start_date = '2025-01-01';
var end_date = '2026-01-01';

var study_area = selected_regions.geometry();


// SENTINEL-2 L1C
var l1c = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(study_area)
    .filterDate(start_date, end_date)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));


// SENTINEL-2 L2A
var l2a = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(study_area)
    .filterDate(start_date, end_date);


// ENCONTRA OS PARES
var join = ee.Join.saveFirst('l2a_image');

var pairs = ee.ImageCollection(
    join.apply({
        primary: l1c,
        secondary: l2a,
        condition: ee.Filter.equals({
            leftField: 'system:index',
            rightField: 'system:index'
        })
    })
);

pairs = pairs.filter(
    ee.Filter.notNull(['l2a_image'])
);


// INFORMACOES
print('Regioes selecionadas:', selected_regions.size());
print('Imagens L1C encontradas:', l1c.size());
print('Imagens L2A encontradas:', l2a.size());
print('Pares L1C + L2A:', pairs.size());

print(
    'IDs dos primeiros pares:',
    pairs.aggregate_array('system:index').slice(0, 10)
);