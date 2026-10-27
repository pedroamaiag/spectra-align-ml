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
var study_area = selected_regions.geometry();

var l1c = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(study_area)
    .filterDate('2025-01-01', '2026-01-01')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));

var l2a = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(study_area)
    .filterDate('2025-01-01', '2026-01-01');


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
).filter(
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

        return pairs
            .filterBounds(region.geometry())
            .map(function (image) {
                return ee.Feature(null, {
                    region_id: region.get('system:index'),
                    pair_id: image.get('system:index'),
                    date: image.date().format('YYYY-MM-dd')
                });
            });
    })
).flatten();


// CLASSIFICA AS ESTACOES
var classified_catalog = catalog.map(function (feature) {
    var month = ee.Date(feature.get('date')).get('month');

    var season = ee.Algorithms.If(
        month.gte(2).and(month.lte(5)),
        'rainy',
        ee.Algorithms.If(
            month.gte(8).and(month.lte(11)),
            'dry',
            'transition'
        )
    );

    return feature.set('season', season);
});


// REMOVE MESES DE TRANSICAO
var final_catalog = classified_catalog.filter(
    ee.Filter.inList('season', ['rainy', 'dry'])
);


// INFORMACOES
print('Total:', final_catalog.size());

print(
    'Chuvoso:',
    final_catalog.filter(
        ee.Filter.eq('season', 'rainy')
    ).size()
);

print(
    'Seco:',
    final_catalog.filter(
        ee.Filter.eq('season', 'dry')
    ).size()
);

print('Primeiros registros:', final_catalog.limit(20));