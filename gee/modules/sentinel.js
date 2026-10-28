// SENTINEL-2 LEVEL-1C
exports.get_l1c = function(area, start_date, end_date) {
    return ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
        .filterBounds(area)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));
};


// SENTINEL-2 LEVEL-2A
exports.get_l2a = function(area, start_date, end_date) {
    return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(area)
        .filterDate(start_date, end_date);
};


// ENCONTRA PARES L1C E L2A
exports.find_pairs = function(l1c, l2a) {
    var join = ee.Join.saveFirst('l2a_image');

    return ee.ImageCollection(
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
};
