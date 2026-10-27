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


// REGIAO DE TESTE
var region = ee.Feature(
    selected_regions.toList(100).get(0)
);


// SENTINEL-2
var l1c = ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(region.geometry())
    .filterDate('2025-01-01', '2026-01-01')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));

var l2a = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(region.geometry())
    .filterDate('2025-01-01', '2026-01-01');


// ENCONTRA PARES
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


// NUVENS DENTRO DA REGIAO
pairs = pairs.map(function (image) {
    var l2a_image = ee.Image(image.get('l2a_image'));
    var scl = l2a_image.select('SCL');

    var cloud_mask = scl.eq(3)
        .or(scl.eq(7))
        .or(scl.eq(8))
        .or(scl.eq(9))
        .or(scl.eq(10))
        .or(scl.eq(11));

    var cloud_fraction = cloud_mask.reduceRegion({
        reducer: ee.Reducer.mean(),
        geometry: region.geometry(),
        scale: 20,
        maxPixels: 1e7
    }).get('SCL');

    return image.set(
        'local_cloud_percentage',
        ee.Number(cloud_fraction).multiply(100)
    );
});


// CLASSIFICA ESTACAO
pairs = pairs.map(function (image) {
    var month = image.date().get('month');

    var season = ee.Algorithms.If(
        month.gte(2).and(month.lte(5)),
        'rainy',
        ee.Algorithms.If(
            month.gte(8).and(month.lte(11)),
            'dry',
            'transition'
        )
    );

    return image.set('season', season);
});


// SEPARA OS PARES
var rainy_pairs = pairs
    .filter(ee.Filter.eq('season', 'rainy'))
    .sort('system:time_start');

var dry_pairs = pairs
    .filter(ee.Filter.eq('season', 'dry'))
    .sort('system:time_start');


// PRIMEIRO PAR DE CADA ESTACAO
var rainy_l1c = ee.Image(rainy_pairs.first());
var rainy_l2a = ee.Image(rainy_l1c.get('l2a_image'));

var dry_l1c = ee.Image(dry_pairs.first());
var dry_l2a = ee.Image(dry_l1c.get('l2a_image'));


// INFORMACOES
print('Region ID:', region.get('system:index'));

print('Pares chuvosos:', rainy_pairs.size());
print('Pares secos:', dry_pairs.size());

print('Par chuvoso:', rainy_l1c.get('system:index'));
print('Par seco:', dry_l1c.get('system:index'));

print(
    'Nuvens nos pares:',
    pairs.aggregate_array('local_cloud_percentage')
);

// EXPORTA L1C CHUVOSO
Export.image.toDrive({
    image: rainy_l1c.select(['B2', 'B3', 'B4', 'B8']),
    description: 'l1c_region_001_rainy',
    folder: 'spectra-align-ml',
    fileNamePrefix: 'l1c_region_001_rainy',
    region: region.geometry(),
    scale: 10,
    crs: 'EPSG:32724',
    maxPixels: 1e9
});


// EXPORTA L2A CHUVOSO
Export.image.toDrive({
    image: rainy_l2a.select(['B2', 'B3', 'B4', 'B8']),
    description: 'l2a_region_001_rainy',
    folder: 'spectra-align-ml',
    fileNamePrefix: 'l2a_region_001_rainy',
    region: region.geometry(),
    scale: 10,
    crs: 'EPSG:32724',
    maxPixels: 1e9
});


// EXPORTA L1C SECO
Export.image.toDrive({
    image: dry_l1c.select(['B2', 'B3', 'B4', 'B8']),
    description: 'l1c_region_001_dry',
    folder: 'spectra-align-ml',
    fileNamePrefix: 'l1c_region_001_dry',
    region: region.geometry(),
    scale: 10,
    crs: 'EPSG:32724',
    maxPixels: 1e9
});


// EXPORTA L2A SECO
Export.image.toDrive({
    image: dry_l2a.select(['B2', 'B3', 'B4', 'B8']),
    description: 'l2a_region_001_dry',
    folder: 'spectra-align-ml',
    fileNamePrefix: 'l2a_region_001_dry',
    region: region.geometry(),
    scale: 10,
    crs: 'EPSG:32724',
    maxPixels: 1e9
});