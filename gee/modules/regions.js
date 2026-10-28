// AREA DE ESTUDO
exports.get_ceara = function() {
    return ee.FeatureCollection('IBGE/UF/V2025')
        .filter(ee.Filter.eq('SIGLA_UF', 'CE'))
        .geometry();
};


// SELECIONA REGIOES DISTRIBUIDAS
exports.select_regions = function(count) {
    var ceara = exports.get_ceara();
    var projection = ee.Projection('EPSG:32724');

    var grid = ceara.coveringGrid({
        proj: projection,
        scale: 5000
    });

    var sectors = ceara.coveringGrid({
        proj: projection,
        scale: 35000
    });

    var randomized_grid = grid.randomColumn('random', 42);

    var distributed_regions = sectors.map(function(sector) {
        var candidates = randomized_grid
            .filterBounds(sector.geometry())
            .sort('random');

        return ee.Algorithms.If(
            candidates.size().gt(0),
            candidates.first(),
            null
        );
    }, true);

    return distributed_regions
        .distinct('system:index')
        .randomColumn('selection', 42)
        .sort('selection')
        .limit(count);
};