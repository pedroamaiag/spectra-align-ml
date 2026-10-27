// AREA DE ESTUDO
var states = ee.FeatureCollection('IBGE/UF/V2025');

var ceara = states
    .filter(ee.Filter.eq('SIGLA_UF', 'CE'))
    .geometry();


// GRADE
var grid_size = 5000;

var projection = ee.Projection('EPSG:32724');

var grid = ceara.coveringGrid({
    proj: projection,
    scale: grid_size
});


// VISUALIZACAO
Map.centerObject(ceara, 7);

Map.addLayer(
    ceara,
    { color: 'red' },
    'Ceara'
);

Map.addLayer(
    grid,
    { color: 'blue' },
    'Grade 5 km'
);


// INFORMACOES
print('Numero de quadrados:', grid.size());
print('Primeiros quadrados:', grid.limit(10));