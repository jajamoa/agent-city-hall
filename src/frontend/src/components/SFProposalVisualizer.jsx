import React, { useState, useEffect, useCallback } from "react";
import Map, { Source, Layer, Marker } from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { MAPBOX_TOKEN } from '../constants/config';
import { api } from '../services/api';
import gridData from '../data/sfZoningGrid.json';
import { generateGridGeoJSON, latLngToGridCoords, updateCell } from '../utils/gridUtils';
import _ from 'lodash';

const SF_COORDINATES = {
  "san_francisco": { longitude: -122.4194, latitude: 37.7749, zoom: 12 },
  "mission": { longitude: -122.4195, latitude: 37.7599, zoom: 14 },
  "soma": { longitude: -122.4010, latitude: 37.7785, zoom: 14 },
  "downtown": { longitude: -122.4194, latitude: 37.7749, zoom: 14 },
  "richmond": { longitude: -122.4784, latitude: 37.7799, zoom: 14 },
  "sunset": { longitude: -122.4862, latitude: 37.7599, zoom: 14 },
  "north_beach": { longitude: -122.4079, latitude: 37.8032, zoom: 14 },
  "marina": { longitude: -122.4367, latitude: 37.8030, zoom: 14 },
  "hayes_valley": { longitude: -122.4241, latitude: 37.7765, zoom: 14 },
  "castro": { longitude: -122.4350, latitude: 37.7609, zoom: 14 }
};

// 高度限制对应的颜色
const heightColors = {
  40: '#FDB462',  // 65 feet
  65: '#FFB6C1',  // 80 feet
  80: '#B3CDE3',  // 85 feet
  85: '#CCEBC5',  // 105 feet
  105: '#DECBE4', // 130 feet
  130: '#FED9A6', // 140 feet
  140: '#FFFFCC', // 240 feet
  240: '#E5D8BD', // 300 feet
  300: '#FDDAEC'  // 300+ feet
};

const TOOLS = {
  // 主要工具
  MAIN: {
    PAN: { id: 'pan', icon: '🖐', label: 'Pan' },
    INSPECT: { id: 'inspect', icon: 'ℹ️', label: 'Inspect' },
    EDIT: { id: 'edit', icon: '✏️', label: 'Edit' }
  },
  // 编辑子工具
  EDIT_SUB: {
    SELECT: { id: 'select', icon: '☝️', label: 'Select' },
    BRUSH: { id: 'brush', icon: '🖌️', label: 'Brush' },
    ERASE: { id: 'erase', icon: '🧹', label: 'Erase' }
  }
};

// 使用React.memo优化渲染性能
const GridCell = React.memo(({ cell, isHovered, isSelected }) => {
  if (!cell?.heightLimit) return null;
  
  return (
    <div
      className={`grid-cell ${isHovered ? 'hovered' : ''} ${isSelected ? 'selected' : ''}`}
      style={{
        backgroundColor: heightColors[cell.heightLimit],
        opacity: isHovered ? 0.8 : 0.6
      }}
    />
  );
});

const SFProposalVisualizer = () => {
  const [viewState, setViewState] = useState({
    ...SF_COORDINATES['san_francisco'],
    padding: { top: 0, bottom: 0, left: 0, right: 0 },
  });
  const [gridCells, setGridCells] = useState(gridData.cells);
  const [selectedCell, setSelectedCell] = useState(null);
  const [currentTool, setCurrentTool] = useState(TOOLS.MAIN.PAN.id);
  const [hoveredCell, setHoveredCell] = useState(null);
  const [showGrid, setShowGrid] = useState(true);
  const [toolbarCollapsed, setToolbarCollapsed] = useState(false);
  const [brushSize, setBrushSize] = useState(1);
  const [selectedHeight, setSelectedHeight] = useState(gridData.heightLimits.default);
  const [isDragging, setIsDragging] = useState(false);
  const [gridConfig] = useState({
    ...gridData.gridConfig,
    bounds: gridData.gridConfig.bounds,
    cellSize: 200
  });
  const [editHistory, setEditHistory] = useState([gridData.cells]); // 历史记录
  const [historyIndex, setHistoryIndex] = useState(0); // 当前历史位置
  const [editMode, setEditMode] = useState(null); // 编辑子模式
  const MAX_HISTORY = 20; // 最大历史记录数量
  const [pendingChanges, setPendingChanges] = useState({}); // 存储未确认的更改
  const [hasUnappliedChanges, setHasUnappliedChanges] = useState(false);
  const mapRef = React.useRef(null);
  const [sourceKey, setSourceKey] = useState(0);

  // 初始化时处理 JSON 中的单元格
  useEffect(() => {
    // 为已有的单元格添加 isEdited 标记
    const initialCells = { ...gridData.cells };
    Object.entries(initialCells).forEach(([key, cell]) => {
      if (cell.heightLimit && cell.heightLimit !== gridData.heightLimits.default) {
        initialCells[key] = {
          ...cell,
          isEdited: true
        };
      }
    });
    setGridCells(initialCells);
    setEditHistory([initialCells]);
    // 强制更新一次
    setSourceKey(prev => prev + 1);
  }, []); // 只在组件挂载时运行一次

  // 生成网格的GeoJSON数据
  const gridGeoJSON = React.useMemo(() => {
    if (!gridConfig.bounds || !showGrid) return null;
    
    const geojson = generateGridGeoJSON(
      {
        ...gridConfig,
        heightLimits: gridData.heightLimits
      },
      gridCells
    );

    // 为每个 feature 添加 key 属性和时间戳
    geojson.features = geojson.features.map(feature => ({
      ...feature,
      properties: {
        ...feature.properties,
        key: `${feature.properties.row}_${feature.properties.col}`,
        timestamp: Date.now()  // 添加时间戳强制更新
      }
    }));

    return geojson;
  }, [gridConfig, gridCells, showGrid]);

  // 应用笔刷编辑
  const applyBrush = useCallback((centerCell) => {
    const { row, col } = centerCell;
    let updatedCells = { ...gridCells };  // 直接修改 gridCells
    let updatedChanges = { ...pendingChanges };
    
    const radius = Math.floor(brushSize / 2);
    for (let r = -radius; r <= radius; r++) {
      for (let c = -radius; c <= radius; c++) {
        const targetRow = row + r;
        const targetCol = col + c;
        
        if (Math.sqrt(r * r + c * c) <= radius) {
          const key = `${targetRow}_${targetCol}`;
          const newHeight = editMode === TOOLS.EDIT_SUB.ERASE.id ? 
            gridData.heightLimits.default : 
            selectedHeight;
            
          // 更新 gridCells 以立即显示效果
          updatedCells[key] = {
            ...updatedCells[key],
            heightLimit: newHeight,
            isEdited: true
          };

          // 记录到 pendingChanges 以便后续存入 history
          updatedChanges[key] = {
            heightLimit: newHeight,
            isPending: true
          };
        }
      }
    }
    
    setGridCells(updatedCells);  // 立即更新显示
    setPendingChanges(updatedChanges);  // 记录待确认的更改
    setHasUnappliedChanges(true);
  }, [gridCells, pendingChanges, brushSize, selectedHeight, editMode]);

  // 处理鼠标移动事件
  const handleMouseMove = useCallback((event) => {
    if (currentTool === TOOLS.MAIN.PAN.id || !gridConfig.bounds) return;

    const [lng, lat] = event.lngLat.toArray();
    const coords = latLngToGridCoords({ lng, lat }, gridConfig);
    
    // 如果坐标没有变化，不更新
    if (hoveredCell?.row === coords.row && hoveredCell?.col === coords.col) {
      return;
    }
    
    setHoveredCell(coords);

    if (isDragging && currentTool === TOOLS.MAIN.EDIT.id && 
        (editMode === TOOLS.EDIT_SUB.BRUSH.id || editMode === TOOLS.EDIT_SUB.ERASE.id)) {
      applyBrush(coords);
    }
  }, [currentTool, editMode, isDragging, gridConfig, hoveredCell, applyBrush]);

  // 处理鼠标按下事件
  const handleMouseDown = useCallback((event) => {
    if (currentTool === TOOLS.MAIN.EDIT.id && 
        (editMode === TOOLS.EDIT_SUB.BRUSH.id || editMode === TOOLS.EDIT_SUB.ERASE.id)) {
      setIsDragging(true);
      // 立即应用第一个笔刷点
      const [lng, lat] = event.lngLat.toArray();
      const coords = latLngToGridCoords({ lng, lat }, gridConfig);
      applyBrush(coords);
    }
  }, [currentTool, editMode, gridConfig, applyBrush]);

  // 处理鼠标抬起事件
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // 处理地图事件
  const handleMapClick = useCallback((event) => {
    if (currentTool === TOOLS.MAIN.PAN.id || !gridConfig.bounds) return;

    const [lng, lat] = event.lngLat.toArray();
    const clickedCell = latLngToGridCoords({ lng, lat }, gridConfig);
    
    switch (currentTool) {
      case TOOLS.MAIN.INSPECT.id:
        setSelectedCell(clickedCell);
        break;
      case TOOLS.MAIN.EDIT.id:
        if (editMode === TOOLS.EDIT_SUB.SELECT.id) {
          setSelectedCell(clickedCell);
          const cell = gridCells[`${clickedCell.row}_${clickedCell.col}`];
          if (cell?.heightLimit) {
            setSelectedHeight(cell.heightLimit);
          }
        } else if (editMode === TOOLS.EDIT_SUB.BRUSH.id || editMode === TOOLS.EDIT_SUB.ERASE.id) {
          applyBrush(clickedCell);
        }
        break;
    }
  }, [currentTool, editMode, gridCells, gridConfig, applyBrush]);

  // 处理单个格子的高度更改
  const handleHeightChange = (height) => {
    setSelectedHeight(height);
    if (height && selectedCell && currentTool === TOOLS.MAIN.EDIT.id && editMode === TOOLS.EDIT_SUB.SELECT.id) {
      const key = `${selectedCell.row}_${selectedCell.col}`;
      // 直接更新 gridCells 显示
      setGridCells(prev => ({
        ...prev,
        [key]: {
          ...prev[key],
          heightLimit: height,
          isEdited: true,
          isPending: true
        }
      }));
      // 记录到 pendingChanges
      setPendingChanges(prev => ({
        ...prev,
        [key]: {
          heightLimit: height,
          isPending: true
        }
      }));
      setHasUnappliedChanges(true);
    }
  };

  // 丢弃更改
  const discardChanges = useCallback(() => {
    // 强制刷新到当前历史状态
    const currentState = editHistory[historyIndex];
    setGridCells({...currentState});  // 使用展开运算符确保引用更新
    setPendingChanges({});
    setHasUnappliedChanges(false);
  }, [editHistory, historyIndex]);

  // 更新工具切换逻辑
  const handleToolChange = (toolId) => {
    if (Object.values(TOOLS.MAIN).some(tool => tool.id === toolId)) {
      // 如果切换到非编辑工具，自动丢弃更改
      if (toolId !== TOOLS.MAIN.EDIT.id && hasUnappliedChanges) {
        discardChanges();
      }
      setCurrentTool(toolId);
      setEditMode(null);
    } else if (Object.values(TOOLS.EDIT_SUB).some(tool => tool.id === toolId)) {
      // 切换编辑子工具时，确保显示状态与缓存一致
      if (hasUnappliedChanges) {
        const currentState = editHistory[historyIndex];
        setGridCells({...currentState});
        setPendingChanges({});
        setHasUnappliedChanges(false);
      }
      setEditMode(toolId);
    }
  };

  // 应用所有待定更改
  const applyChanges = useCallback(() => {
    if (!hasUnappliedChanges) return;

    const updatedCells = { ...gridCells };
    Object.entries(pendingChanges).forEach(([key, change]) => {
      if (change.isPending) {
        const [row, col] = key.split('_').map(Number);
        updatedCells[key] = {
          ...updatedCells[key],
          heightLimit: change.heightLimit,
          isEdited: true,
          lastUpdated: new Date().toISOString().split('T')[0]
        };
      }
    });

    // 保存到历史记录
    const newHistory = editHistory.slice(0, historyIndex + 1);
    newHistory.push(updatedCells);
    if (newHistory.length > MAX_HISTORY) {
      newHistory.shift();
      // 调整 historyIndex 以适应移除的记录
      setHistoryIndex(prev => prev - 1);
    }
    setEditHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);

    setGridCells(updatedCells);
    setPendingChanges({});
    setHasUnappliedChanges(false);
  }, [gridCells, pendingChanges, hasUnappliedChanges, editHistory, historyIndex]);

  // 撤销
  const undo = useCallback(() => {
    if (historyIndex > 0) {
      const newState = editHistory[historyIndex - 1];
      setGridCells({...newState});  // 强制刷新显示
      setPendingChanges({});
      setHasUnappliedChanges(false);
      setHistoryIndex(historyIndex - 1);
    }
  }, [historyIndex, editHistory]);

  // 重做
  const redo = useCallback(() => {
    if (historyIndex < editHistory.length - 1) {
      const newState = editHistory[historyIndex + 1];
      setGridCells({...newState});  // 强制刷新显示
      setPendingChanges({});
      setHasUnappliedChanges(false);
      setHistoryIndex(historyIndex + 1);
    }
  }, [historyIndex, editHistory]);

  // 更新网格样式以显示编辑状态
  const gridLayerStyle = {
    id: 'grid-fill',
    type: 'fill',
    paint: {
      'fill-color': [
        'case',
        // 检查是否是编辑中的格子
        ['in', ['get', 'key'], ...Object.keys(pendingChanges)],
        [
          'match',
          ['get', 'key'],
          ...Object.entries(pendingChanges).flatMap(([key, change]) => [key, heightColors[change.heightLimit]]),
          'transparent'
        ],
        // 如果不是编辑中的格子，使用当前状态的颜色
        ['has', 'heightLimit'],
        [
          'match',
          ['get', 'heightLimit'],
          ...Object.entries(heightColors).flatMap(([height, color]) => [parseInt(height), color]),
          'transparent'
        ],
        'transparent'
      ],
      'fill-opacity': [
        'case',
        // 编辑中的格子使用更高的透明度
        ['in', ['get', 'key'], ...Object.keys(pendingChanges)],
        0.8,
        // hover 的格子
        ['all',
          ['==', ['get', 'row'], hoveredCell?.row],
          ['==', ['get', 'col'], hoveredCell?.col]
        ],
        0.8,
        // 其他格子
        0.6
      ]
    }
  };

  // 暂时注释掉 pattern 图层，等颜色显示正常后再处理
  const editingLayerStyle = {
    id: 'editing-pattern',
    type: 'fill',
    paint: {
      'fill-color': '#fff',
      'fill-opacity': 0.1
    },
    filter: ['in', ['get', 'key'], ...Object.keys(pendingChanges)]
  };

  // 添加一个基础网格图层，显示所有网格
  const baseGridLayerStyle = {
    id: 'base-grid',
    type: 'fill',
    paint: {
      'fill-color': '#000',
      'fill-opacity': [
        'case',
        ['all',
          ['==', ['get', 'row'], hoveredCell?.row],
          ['==', ['get', 'col'], hoveredCell?.col]
        ],
        0.2,
        0
      ]
    }
  };

  const gridOutlineStyle = {
    id: 'grid-outline',
    type: 'line',
    paint: {
      'line-color': '#000',
      'line-width': 0.5,
      'line-opacity': 0.2,
      'line-gap-width': 0
    }
  };

  // 使用防抖优化鼠标移动事件，但降低延迟以提高响应性
  const debouncedMouseMove = useCallback(
    _.debounce((event) => {
      handleMouseMove(event);
    }, 8), // 降低延迟到8ms
    [handleMouseMove]
  );

  // 修改 pattern 加载逻辑
  useEffect(() => {
    const map = mapRef.current?.getMap();
    if (!map) return;

    const loadPattern = () => {
      // 检查 pattern 是否已存在
      if (map.hasImage('editing-pattern')) return;

      const img = new Image();
      img.onload = () => {
        // 确保地图仍然存在
        if (map.hasImage('editing-pattern')) return;
        map.addImage('editing-pattern', img);
      };
      img.src = 'data:image/svg+xml;base64,' + btoa(`
        <svg width='8' height='8' viewBox='0 0 8 8' xmlns='http://www.w3.org/2000/svg'>
          <path d='M-1,1 l2,-2 M0,8 l8,-8 M7,9 l2,-2' stroke='rgba(255,255,255,0.5)' stroke-width='1'/>
        </svg>
      `);
    };

    // 如果地图已加载，直接添加 pattern
    if (map.loaded()) {
      loadPattern();
    } else {
      // 否则等待地图加载完成
      map.once('load', loadPattern);
    }

    // 清理函数
    return () => {
      const map = mapRef.current?.getMap();
      if (map && map.hasImage('editing-pattern')) {
        map.removeImage('editing-pattern');
      }
    };
  }, []);

  return (
    <div className="sf-visualizer-container">
      <div className={`toolbar ${toolbarCollapsed ? 'collapsed' : ''}`}>
        <div className="toolbar-header">
          <h3>Tools</h3>
          <button
            className="collapse-button"
            onClick={() => setToolbarCollapsed(!toolbarCollapsed)}
          >
            {toolbarCollapsed ? '>' : '<'}
          </button>
        </div>
        
        {!toolbarCollapsed && (
          <div className="toolbar-content">
            <div className="tool-section">
              <label className="tool-label">Grid Visibility</label>
              <button
                className={`dark-button ${showGrid ? 'active' : ''}`}
                onClick={() => {
                  setShowGrid(!showGrid);
                  // 强制触发一次 Source 更新
                  setSourceKey(prev => prev + 1);
                }}
              >
                {showGrid ? 'Hide Grid' : 'Show Grid'}
              </button>
            </div>

            <div className="tool-section">
              <label className="tool-label">Main Tools</label>
              <div className="tool-buttons">
                {Object.values(TOOLS.MAIN).map(tool => (
                  <button
                    key={tool.id}
                    className={`dark-button ${currentTool === tool.id ? 'active' : ''}`}
                    onClick={() => handleToolChange(tool.id)}
                    title={`${tool.label} Tool (${tool.icon})`}
                  >
                    {tool.icon} {tool.label}
                  </button>
                ))}
              </div>
            </div>

            {currentTool === TOOLS.MAIN.EDIT.id && (
              <>
                <div className="tool-section">
                  <label className="tool-label">Edit Tools</label>
                  <div className="tool-buttons">
                    {Object.values(TOOLS.EDIT_SUB).map(tool => (
                      <button
                        key={tool.id}
                        className={`dark-button ${editMode === tool.id ? 'active' : ''}`}
                        onClick={() => handleToolChange(tool.id)}
                        title={`${tool.label} Tool (${tool.icon})`}
                      >
                        {tool.icon} {tool.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="tool-section">
                  <label className="tool-label">History</label>
                  <div className="tool-buttons">
                    <button
                      className="dark-button"
                      onClick={undo}
                      disabled={historyIndex <= 0}
                      title="Undo"
                    >
                      ↩️ Undo
                    </button>
                    <button
                      className="dark-button"
                      onClick={redo}
                      disabled={historyIndex >= editHistory.length - 1}
                      title="Redo"
                    >
                      ↪️ Redo
                    </button>
                  </div>
                </div>

                {(editMode === TOOLS.EDIT_SUB.SELECT.id || editMode === TOOLS.EDIT_SUB.BRUSH.id) && (
                  <div className="tool-section">
                    <label className="tool-label">Height Limit</label>
                    <select
                      value={selectedHeight || ''}
                      onChange={(e) => handleHeightChange(e.target.value ? parseInt(e.target.value) : null)}
                      className="dark-input"
                    >
                      <option value="">-- Select Height --</option>
                      {gridData.heightLimits.options.map(height => (
                        <option key={height} value={height}>{height} feet</option>
                      ))}
                    </select>
                  </div>
                )}

                {(editMode === TOOLS.EDIT_SUB.BRUSH.id || editMode === TOOLS.EDIT_SUB.ERASE.id) && (
                  <div className="tool-section">
                    <label className="tool-label">Brush Size: {brushSize}</label>
                    <input
                      type="range"
                      min="1"
                      max="5"
                      value={brushSize}
                      onChange={(e) => setBrushSize(parseInt(e.target.value))}
                      className="brush-size-slider"
                    />
                  </div>
                )}

                {hasUnappliedChanges && (
                  <div className="tool-section">
                    <div className="edit-actions">
                      <button
                        className="dark-button apply-button"
                        onClick={applyChanges}
                      >
                        Apply Changes
                      </button>
                      <button
                        className="dark-button"
                        onClick={discardChanges}
                      >
                        Discard Changes
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>

      <div className="main-content">
        <Map
          ref={mapRef}
          {...viewState}
          onMove={(evt) => currentTool === TOOLS.MAIN.PAN.id && setViewState(evt.viewState)}
          onClick={handleMapClick}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseMove={debouncedMouseMove}
          dragPan={currentTool === TOOLS.MAIN.PAN.id}
          dragRotate={currentTool === TOOLS.MAIN.PAN.id}
          scrollZoom={currentTool === TOOLS.MAIN.PAN.id}
          style={{ width: "100%", height: "100%" }}
          mapStyle="mapbox://styles/mapbox/dark-v10"
          mapboxAccessToken={MAPBOX_TOKEN}
          cursor={
            currentTool === TOOLS.MAIN.PAN.id ? (isDragging ? 'grabbing' : 'grab') :
            currentTool === TOOLS.MAIN.INSPECT.id ? 'pointer' :
            currentTool === TOOLS.MAIN.EDIT.id ? (
              editMode === TOOLS.EDIT_SUB.SELECT.id ? 'pointer' :
              editMode === TOOLS.EDIT_SUB.BRUSH.id || editMode === TOOLS.EDIT_SUB.ERASE.id ? 'crosshair' :
              'default'
            ) : 'default'
          }
        >
          {showGrid && gridGeoJSON && (
            <Source 
              key={sourceKey}
              type="geojson" 
              data={gridGeoJSON}
            >
              <Layer {...baseGridLayerStyle} />
              <Layer {...gridLayerStyle} />
              {/* <Layer {...editingLayerStyle} /> */}
              <Layer {...gridOutlineStyle} />
            </Source>
          )}
        </Map>
      </div>

      {selectedCell && (currentTool === TOOLS.MAIN.INSPECT.id || currentTool === TOOLS.MAIN.EDIT.id) && (
        <div className="detail-panel">
          <div className="detail-panel-header">
            <h4>Cell Details</h4>
            <button
              className="close-button"
              onClick={() => setSelectedCell(null)}
            >
              ×
            </button>
          </div>
          <div className="detail-content">
            <div className="detail-row">
              <span className="detail-label">Location:</span>
              <span>Row {selectedCell.row}, Col {selectedCell.col}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Height Limit:</span>
              <span>{gridCells[`${selectedCell.row}_${selectedCell.col}`]?.heightLimit || gridData.heightLimits.default} feet</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Category:</span>
              <span>{gridCells[`${selectedCell.row}_${selectedCell.col}`]?.category || 'unzoned'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Last Updated:</span>
              <span>{gridCells[`${selectedCell.row}_${selectedCell.col}`]?.lastUpdated || 'Never'}</span>
            </div>
          </div>
        </div>
      )}

      <div className="legend-panel">
        <h4>Height Limits</h4>
        <div className="height-legend">
          {Object.entries(heightColors).map(([height, color]) => (
            <div key={height} className="legend-item">
              <div className="color-box" style={{ backgroundColor: color }} />
              <span>{height} feet</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default React.memo(SFProposalVisualizer); 