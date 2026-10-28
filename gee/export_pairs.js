
var regions = require(
    'users/pedroamaiag/spectra-align-ml:modules/regions'
);

var sentinel = require(
    'users/pedroamaiag/spectra-align-ml:modules/sentinel'
);

var clouds = require(
    'users/pedroamaiag/spectra-align-ml:modules/clouds'
);


// CONFIGURACAO
var region_count = 5;
var max_cloud_percentage = 10;
var no_data_value = -9999;
var export_enabled = true;

var bands = ['B2', 'B3', 'B4', 'B8'];
var start_date = '2025-01-01';
var end_date = '2026-01-01';

var selected_regions = regions.select_regions(100);
var region_list = selected_regions.toList(region_count);


// CLASSIFICA ESTACAO
function add_season(image) {
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
}


// EXPORTA IMAGEM
function export_raster(image, geometry, name) {
    Export.image.toDrive({
        image: image,
        description: name,
        folder: 'spectra-align-ml',
        fileNamePrefix: name,
        region: geometry,
        scale: 10,
        crs: 'EPSG:32724',
        maxPixels: 1e9,
        fileFormat: 'GeoTIFF',
        formatOptions: {
            noData: no_data_value
        }
    });
}


// PREPARA E EXPORTA UM PAR
function export_pair(pairs, count, geometry, region_name, season) {
    if (count === 0) {
        print(region_name + ' / ' + season + ': sem pares');
        return;
    }

    var l1c_image = ee.Image(pairs.first());
    var l2a_image = ee.Image(l1c_image.get('l2a_image'));

    print(
        region_name + ' / ' + season + ' / ID:',
        l1c_image.get('system:index')
    );

    print(
        region_name + ' / ' + season + ' / nuvens (%):',
        l1c_image.get('local_cloud_percentage')
    );

    if (!export_enabled) {
        return;
    }

    var mask = clouds.get_valid_mask(l2a_image);

    var l1c_export = l1c_image
        .select(bands)
        .updateMask(mask)
        .toFloat()
        .unmask(no_data_value, false);

    var l2a_export = l2a_image
        .select(bands)
        .updateMask(mask)
        .toFloat()
        .unmask(no_data_value, false);

    export_raster(
        l1c_export,
        geometry,
        'l1c_' + region_name + '_' + season + '_masked'
    );

    export_raster(
        l2a_export,
        geometry,
        'l2a_' + region_name + '_' + season + '_masked'
    );
}


// PROCESSA UMA REGIAO
function process_region(index) {
    var region = ee.Feature(region_list.get(index));
    var geometry = region.geometry();

    var region_name = 'region_' +
        ('00' + (index + 1)).slice(-3);

    var l1c = sentinel.get_l1c(
        geometry, start_date, end_date
    );

    var l2a = sentinel.get_l2a(
        geometry, start_date, end_date
    );

    var pairs = sentinel.find_pairs(l1c, l2a);

    pairs = pairs.map(function(image) {
        return clouds.add_cloud_percentage(image, geometry);
    });

    pairs = pairs.map(add_season);

    var clear_pairs = pairs.filter(
        ee.Filter.lte(
            'local_cloud_percentage',
            max_cloud_percentage
        )
    );

    var rainy_pairs = clear_pairs
        .filter(ee.Filter.eq('season', 'rainy'))
        .sort('local_cloud_percentage');

    var dry_pairs = clear_pairs
        .filter(ee.Filter.eq('season', 'dry'))
        .sort('local_cloud_percentage');

    var statistics = ee.Dictionary({
        total: pairs.size(),
        approved: clear_pairs.size(),
        rainy: rainy_pairs.size(),
        dry: dry_pairs.size()
    });

    print(region_name + ' / grid ID:',
        region.get('system:index'));

    statistics.evaluate(function(result, error) {
        if (error) {
            print(region_name + ' / erro:', error);
            return;
        }

        print(region_name + ' / estatisticas:', result);

        export_pair(
            rainy_pairs,
            result.rainy,
            geometry,
            region_name,
            'rainy'
        );

        export_pair(
            dry_pairs,
            result.dry,
            geometry,
            region_name,
            'dry'
        );
    });
}


// EXECUCAO
for (var i = 0; i < region_count; i++) {
    process_region(i);
}