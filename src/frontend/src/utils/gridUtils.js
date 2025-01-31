// 将经纬度转换为网格坐标
export const latLngToGridCoords = (lngLat, config) => {
  const { bounds, cellSize } = config;
  const { lng, lat } = lngLat;

  // Calculate the area dimensions in meters
  const width = (bounds.east - bounds.west) * 111319.9 * Math.cos((bounds.north + bounds.south) / 2 * Math.PI / 180);
  const height = (bounds.north - bounds.south) * 111319.9;

  // Calculate grid dimensions
  const gridWidth = Math.floor(width / cellSize);
  const gridHeight = Math.floor(height / cellSize);

  // Calculate padding
  const widthPadding = (bounds.east - bounds.west) * (1 - gridWidth * cellSize / width) / 2;
  const heightPadding = (bounds.north - bounds.south) * (1 - gridHeight * cellSize / height) / 2;

  // Adjust bounds with padding
  const effectiveBounds = {
    west: bounds.west + widthPadding,
    east: bounds.east - widthPadding,
    north: bounds.north - heightPadding,
    south: bounds.south + heightPadding
  };

  // Calculate position relative to effective bounds
  const x = (lng - effectiveBounds.west) / (effectiveBounds.east - effectiveBounds.west);
  const y = (lat - effectiveBounds.south) / (effectiveBounds.north - effectiveBounds.south);

  const col = Math.floor(x * gridWidth);
  const row = Math.floor((1 - y) * gridHeight);

  return {
    row: Math.max(0, Math.min(row, gridHeight - 1)),
    col: Math.max(0, Math.min(col, gridWidth - 1))
  };
};

// 将网格坐标转换为经纬度（返回网格中心点）
export const gridCoordsToLatLng = (row, col, gridConfig) => {
  const { cellSize, bounds } = gridConfig;
  
  const lat = bounds.north - (row + 0.5) * cellSize / 111000;
  const lng = bounds.west + (col + 0.5) * cellSize / (111000 * Math.cos(lat * Math.PI / 180));
  
  return { lat, lng };
};

// 获取网格单元格信息
export const getCellInfo = (row, col, cells, defaultHeight) => {
  const key = `${row}_${col}`;
  return cells[key] || {
    heightLimit: defaultHeight,
    category: "unzoned",
    lastUpdated: null
  };
};

// 更新网格单元格信息
export const updateCell = (row, col, newData, cells) => {
  const key = `${row}_${col}`;
  return {
    ...cells,
    [key]: {
      ...cells[key],
      ...newData,
      lastUpdated: new Date().toISOString().split('T')[0],
      isEdited: true  // 添加编辑标记
    }
  };
};

// 生成网格的GeoJSON数据
export const generateGridGeoJSON = (config, cells) => {
  const { bounds, cellSize } = config;
  const features = [];

  // Calculate the area dimensions in meters
  const width = (bounds.east - bounds.west) * 111319.9 * Math.cos((bounds.north + bounds.south) / 2 * Math.PI / 180);
  const height = (bounds.north - bounds.south) * 111319.9;

  // Calculate grid dimensions
  const gridWidth = Math.floor(width / cellSize);
  const gridHeight = Math.floor(height / cellSize);

  // Calculate padding
  const widthPadding = (bounds.east - bounds.west) * (1 - gridWidth * cellSize / width) / 2;
  const heightPadding = (bounds.north - bounds.south) * (1 - gridHeight * cellSize / height) / 2;

  // Adjust bounds with padding
  const effectiveBounds = {
    west: bounds.west + widthPadding,
    east: bounds.east - widthPadding,
    north: bounds.north - heightPadding,
    south: bounds.south + heightPadding
  };

  const cellWidth = (effectiveBounds.east - effectiveBounds.west) / gridWidth;
  const cellHeight = (effectiveBounds.north - effectiveBounds.south) / gridHeight;

  // 生成所有网格单元
  for (let row = 0; row < gridHeight; row++) {
    for (let col = 0; col < gridWidth; col++) {
      const cell = cells[`${row}_${col}`];
      const west = effectiveBounds.west + col * cellWidth;
      const east = effectiveBounds.west + (col + 1) * cellWidth;
      const south = effectiveBounds.north - (row + 1) * cellHeight;
      const north = effectiveBounds.north - row * cellHeight;

      // 判断是否被编辑过（包括初始JSON中指定的值）
      const isEdited = cell?.isEdited || (cell?.heightLimit && cell.heightLimit !== config.heightLimits.default);

      features.push({
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [[
            [west, south],
            [east, south],
            [east, north],
            [west, north],
            [west, south]
          ]]
        },
        properties: {
          row,
          col,
          ...(cell || {}),
          heightLimit: cell?.heightLimit || config.heightLimits.default,
          isEdited
        }
      });
    }
  }

  return {
    type: 'FeatureCollection',
    features
  };
}; 