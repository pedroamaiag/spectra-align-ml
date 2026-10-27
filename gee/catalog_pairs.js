// AREA DE ESTUDO
var states = ee.FeatureCollection('IBGE/UF/V2025');

var ceara = states
    .filter(ee.Filter.eq('SIGLA_UF', 'CE'))
    .geometry();


// GRADE
var projection = ee.Projection('EPSG:32724');

var grid = ceara.coveringGrid({
    proj: projection,
    scale: 5000
});

var sectors = ceara.coveringGrid({
    proj: projection,
    scale: 35000
});


// SELECIONA 100 REGIOES
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

var selected_regions = distributed_regions
    .randomColumn('selection', 42)
    .sort('selection')
    .limit(100);


// SENTINEL-2
var start_date = '2025-01-01';
var end_date = '2026-01-01';

var study_area = selected_regions.geometry();

var l1c = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(study_area)
    .filterDate(start_date, end_date)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));

var l2a = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(study_area)
    .filterDate(start_date, end_date);


// PARES
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


// CATALOGO
var region_list = selected_regions.toList(
    selected_regions.size()
);

var indexes = ee.List.sequence(
    0,
    selected_regions.size().subtract(1)
);

var catalog = ee.FeatureCollection(
    indexes.map(function (index) {
        var region = ee.Feature(region_list.get(index));

        var region_id = region.get('system:index');

        return pairs
            .filterBounds(region.geometry())
            .map(function (image) {
                return ee.Feature(null, {
                    region_id: region_id,
                    pair_id: image.get('system:index'),
                    date: image.date().format('YYYY-MM-dd')
                });
            });
    })
).flatten();


// INFORMACOES
print('Total de registros:', catalog.size());
print('Primeiros registros:', catalog.limit(20));
print('Primeiro registro:', catalog.first());
print(
    'Propriedades:',
    ee.Feature(catalog.first()).propertyNames()
);