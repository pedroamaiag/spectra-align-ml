// MASCARA PIXELS INVALIDOS
exports.get_valid_mask = function(l2a_image) {
    var scl = l2a_image.select('SCL');

    return scl.neq(0)
        .and(scl.neq(1))
        .and(scl.neq(3))
        .and(scl.neq(7))
        .and(scl.neq(8))
        .and(scl.neq(9))
        .and(scl.neq(10))
        .and(scl.neq(11));
};


// CALCULA COBERTURA LOCAL
exports.add_cloud_percentage = function(image, geometry) {
    var l2a_image = ee.Image(image.get('l2a_image'));
    var scl = l2a_image.select('SCL');

    var valid_scl = scl.neq(0).and(scl.neq(1));

    var cloud_mask = scl.eq(3)
        .or(scl.eq(7))
        .or(scl.eq(8))
        .or(scl.eq(9))
        .or(scl.eq(10))
        .or(scl.eq(11));

    var stats = cloud_mask
        .updateMask(valid_scl)
        .reduceRegion({
            reducer: ee.Reducer.mean(),
            geometry: geometry,
            scale: 20,
            crs: 'EPSG:32724',
            maxPixels: 1e7
        });

    var fraction = ee.Number(stats.get('SCL', 1));

    return image.set(
        'local_cloud_percentage',
        fraction.multiply(100)
    );
};
