import React, { useState, useEffect, useCallback, forwardRef, useImperativeHandle } from "react";
import Map, { Source, Layer, Marker } from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { MAPBOX_TOKEN } from '../constants/config';
import { api } from '../services/api';
// import gridData from '../data/sfZoningGrid.json';
import gridData from '../data/sfZoningGrid2024.json';
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

// Height limit colors
const heightColors = {
  65: '#F4A261',  // 65 feet (6 stories) - Soft Orange
  80: '#D291FF',  // 80 feet (Unchanged) - Pastel Purple
  85: '#E76F51',  // 85 feet (8 stories) - Vibrant Orange-Red
  105: '#C642E3', // 105 feet (Unchanged) - Bright Magenta
  130: '#32127A', // 130 feet (Unchanged) - Deep Purple
  140: '#E63946', // 140 feet (14 stories) - Intense Red
  240: '#A93226', // 240 feet (24 stories) - Dark Crimson
  300: '#6B4226'  // 300 feet (30 stories) - Rich Brown
};

const TOOLS = {
  // Main tools
  MAIN: {
    PAN: { id: 'pan', icon: '🖐', label: 'Pan' },
    INSPECT: { id: 'inspect', icon: 'ℹ️', label: 'Inspect' },
    EDIT: { id: 'edit', icon: '✏️', label: 'Edit' }
  },
  // Edit sub-tools
  EDIT_SUB: {
    SELECT: { id: 'select', icon: '☝️', label: 'Select' },
    BRUSH: { id: 'brush', icon: '🖌️', label: 'Brush' },
    ERASE: { id: 'erase', icon: '🧹', label: 'Erase' }
  }
};

// Optimize rendering performance using React.memo
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

const MAX_HISTORY = 20; // Maximum number of history records

const STORAGE_KEY = 'sf_zoning_grid_data';

const SFProposalVisualizer = forwardRef(({ map, onMapInteraction }, ref) => {
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
    cellSize: gridData.gridConfig.cellSize || 100,
    bounds: gridData.gridConfig.bounds
  });
  const [editHistory, setEditHistory] = useState([gridData.cells]);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [editMode, setEditMode] = useState(null);
  const [pendingChanges, setPendingChanges] = useState({});
  const [hasUnappliedChanges, setHasUnappliedChanges] = useState(false);
  const [sourceKey, setSourceKey] = useState(0);

  // Initialize pattern
  useEffect(() => {
    if (!map) return;

    const loadPattern = () => {
      if (map.hasImage('editing-pattern')) return;

      const img = new Image();
      img.onload = () => {
        if (map.hasImage('editing-pattern')) return;
        map.addImage('editing-pattern', img);
      };
      img.src = 'data:image/svg+xml;base64,' + btoa(`
        <svg width='8' height='8' viewBox='0 0 8 8' xmlns='http://www.w3.org/2000/svg'>
          <path d='M-1,1 l2,-2 M0,8 l8,-8 M7,9 l2,-2' stroke='rgba(255,255,255,0.5)' stroke-width='1'/>
        </svg>
      `);
    };

    if (map.loaded()) {
      loadPattern();
    } else {
      map.once('load', loadPattern);
    }

    return () => {
      if (map && map.hasImage('editing-pattern')) {
        map.removeImage('editing-pattern');
      }
    };
  }, [map]);

  // Initialize data
  useEffect(() => {
    // First try to load data from localStorage
    const savedData = localStorage.getItem(STORAGE_KEY);
    // Use deep copy to avoid reference issues
    let initialCells = JSON.parse(JSON.stringify(gridData.cells));

    if (savedData) {
      try {
        const parsedData = JSON.parse(savedData);
        // Merge saved data with default data
        initialCells = {
          ...initialCells,
          ...parsedData
        };
      } catch (error) {
        console.error('Error loading saved grid data:', error);
      }
    } else {
      // If no saved data, mark edited cells in initial JSON
      Object.entries(initialCells).forEach(([key, cell]) => {
        if (cell.heightLimit && cell.heightLimit !== gridData.heightLimits.default) {
          initialCells[key] = {
            ...cell,
            isEdited: true
          };
        }
      });
    }

    setGridCells(initialCells);
    setEditHistory([initialCells]);
  }, []); // Only run once when component mounts

  // Generate GeoJSON data
  const gridGeoJSON = React.useMemo(() => {
    if (!gridConfig.bounds || !showGrid) return null;
    
    const geojson = generateGridGeoJSON(
      {
        cellSize: gridConfig.cellSize,
        bounds: gridConfig.bounds,
        heightLimits: gridData.heightLimits
      },
      gridCells
    );

    return geojson;
  }, [gridConfig, gridCells, showGrid]);

  // Apply brush edits
  const applyBrush = useCallback((centerCell) => {
    const { row, col } = centerCell;
    let updatedCells = { ...gridCells };  // Directly modify gridCells
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
            
          // Update gridCells for immediate display
          updatedCells[key] = {
            ...updatedCells[key],
            heightLimit: newHeight,
            isEdited: true
          };

          // Record to pendingChanges for later history
          updatedChanges[key] = {
            heightLimit: newHeight,
            isPending: true
          };
        }
      }
    }
    
    setGridCells(updatedCells);  // Update display immediately
    setPendingChanges(updatedChanges);  // Record pending changes
    setHasUnappliedChanges(true);
  }, [gridCells, pendingChanges, brushSize, selectedHeight, editMode]);

  // Handle mouse move events
  const handleMouseMove = useCallback((event) => {
    if (currentTool === TOOLS.MAIN.PAN.id || !gridConfig.bounds) return;

    const [lng, lat] = event.lngLat.toArray();
    const coords = latLngToGridCoords({ lng, lat }, gridConfig);
    
    // Don't update if coordinates haven't changed
    if (hoveredCell?.row === coords.row && hoveredCell?.col === coords.col) {
      return;
    }
    
    setHoveredCell(coords);

    if (isDragging && currentTool === TOOLS.MAIN.EDIT.id && 
        (editMode === TOOLS.EDIT_SUB.BRUSH.id || editMode === TOOLS.EDIT_SUB.ERASE.id)) {
      applyBrush(coords);
    }
  }, [currentTool, editMode, isDragging, gridConfig, hoveredCell, applyBrush]);

  // Handle mouse down events
  const handleMouseDown = useCallback((event) => {
    if (currentTool === TOOLS.MAIN.EDIT.id && 
        (editMode === TOOLS.EDIT_SUB.BRUSH.id || editMode === TOOLS.EDIT_SUB.ERASE.id)) {
      setIsDragging(true);
      // Immediately apply first brush point
      const [lng, lat] = event.lngLat.toArray();
      const coords = latLngToGridCoords({ lng, lat }, gridConfig);
      applyBrush(coords);
    }
  }, [currentTool, editMode, gridConfig, applyBrush]);

  // Handle mouse up events
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Handle map click events
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

  // Handle single cell height change
  const handleHeightChange = (height) => {
    setSelectedHeight(height);
    if (height && selectedCell && currentTool === TOOLS.MAIN.EDIT.id && editMode === TOOLS.EDIT_SUB.SELECT.id) {
      const key = `${selectedCell.row}_${selectedCell.col}`;
      // Directly update gridCells display
      setGridCells(prev => ({
        ...prev,
        [key]: {
          ...prev[key],
          heightLimit: height,
          isEdited: true,
          isPending: true
        }
      }));
      // Record to pendingChanges
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

  // Discard changes
  const discardChanges = useCallback(() => {
    // Force refresh to current history state
    const currentState = editHistory[historyIndex];
    setGridCells({...currentState});  // Use spread operator to ensure reference update
    setPendingChanges({});
    setHasUnappliedChanges(false);
  }, [editHistory, historyIndex]);

  // Update tool switching logic
  const handleToolChange = (toolId) => {
    if (Object.values(TOOLS.MAIN).some(tool => tool.id === toolId)) {
      // If switching to non-edit tool, automatically discard changes
      if (toolId !== TOOLS.MAIN.EDIT.id && hasUnappliedChanges) {
        discardChanges();
      }
      setCurrentTool(toolId);
      setEditMode(null);
      // Notify parent component map interaction status
      onMapInteraction(toolId === TOOLS.MAIN.PAN.id);
    } else if (Object.values(TOOLS.EDIT_SUB).some(tool => tool.id === toolId)) {
      // Ensure display state consistent with cache when switching edit sub-tools
      if (hasUnappliedChanges) {
        const currentState = editHistory[historyIndex];
        setGridCells({...currentState});
        setPendingChanges({});
        setHasUnappliedChanges(false);
      }
      setEditMode(toolId);
    }
  };

  // Modify applyChanges function, add persistence logic
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

    // Save to history
    const newHistory = editHistory.slice(0, historyIndex + 1);
    newHistory.push(updatedCells);
    if (newHistory.length > MAX_HISTORY) {
      newHistory.shift();
      // Adjust historyIndex to adapt to removed record
      setHistoryIndex(prev => prev - 1);
    }
    setEditHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);

    setGridCells(updatedCells);
    setPendingChanges({});
    setHasUnappliedChanges(false);

    // Persist to localStorage
    try {
      // Only save modified cells
      const modifiedCells = {};
      Object.entries(updatedCells).forEach(([key, cell]) => {
        if (cell.isEdited) {
          modifiedCells[key] = cell;
        }
      });
      localStorage.setItem(STORAGE_KEY, JSON.stringify(modifiedCells));
    } catch (error) {
      console.error('Error saving grid data:', error);
    }
  }, [gridCells, pendingChanges, hasUnappliedChanges, editHistory, historyIndex]);

  // Add reset functionality
  const resetToDefault = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setGridCells(gridData.cells);
    setEditHistory([gridData.cells]);
    setHistoryIndex(0);
    setPendingChanges({});
    setHasUnappliedChanges(false);
    setSelectedCell(null);
  }, []);

  // Undo
  const undo = useCallback(() => {
    if (historyIndex > 0) {
      const newState = editHistory[historyIndex - 1];
      setGridCells({...newState});  // Force refresh display
      setPendingChanges({});
      setHasUnappliedChanges(false);
      setHistoryIndex(historyIndex - 1);
    }
  }, [historyIndex, editHistory]);

  // Redo
  const redo = useCallback(() => {
    if (historyIndex < editHistory.length - 1) {
      const newState = editHistory[historyIndex + 1];
      setGridCells({...newState});  // Force refresh display
      setPendingChanges({});
      setHasUnappliedChanges(false);
      setHistoryIndex(historyIndex + 1);
    }
  }, [historyIndex, editHistory]);

  // Use debounce for mouse move events, but reduce delay for responsiveness
  const debouncedMouseMove = useCallback(
    _.debounce((event) => {
      handleMouseMove(event);
    }, 8), // Reduce delay to 8ms
    [handleMouseMove]
  );

  // Update grid style to display edit status
  const gridLayerStyle = {
    id: 'grid-fill',
    type: 'fill',
    paint: {
      'fill-color': [
        'match',
        ['get', 'heightLimit'],
        65, heightColors[65],
        80, heightColors[80],
        85, heightColors[85],
        105, heightColors[105],
        130, heightColors[130],
        140, heightColors[140],
        240, heightColors[240],
        300, heightColors[300],
        'transparent'  // default color
      ],
      'fill-opacity': 0.6
    }
  };

  // Temporarily comment out pattern layer until color display is normal
  const editingLayerStyle = {
    id: 'editing-pattern',
    type: 'fill',
    paint: {
      'fill-color': '#fff',
      'fill-opacity': 0.1
    },
    filter: ['in', ['get', 'key'], ...Object.keys(pendingChanges)]
  };

  // Add a base grid layer to display all grids
  const baseGridLayerStyle = {
    id: 'base-grid',
    type: 'fill',
    paint: {
      'fill-color': '#000',
      'fill-opacity': 0.05
    }
  };

  const gridOutlineStyle = {
    id: 'grid-outline',
    type: 'line',
    paint: {
      'line-color': '#000',
      'line-width': 0.5,
      'line-opacity': 0.1
    }
  };

  // Modify Grid Visibility button processing function
  const toggleGridVisibility = useCallback(() => {
    setShowGrid(prev => !prev);
  }, []);

  // Expose methods to parent component
  useImperativeHandle(ref, () => ({
    handleMapClick: handleMapClick,
    handleMouseDown: handleMouseDown,
    handleMouseUp: handleMouseUp,
    handleMouseMove: debouncedMouseMove,
    getCursor: () => {
      return currentTool === TOOLS.MAIN.PAN.id ? (isDragging ? 'grabbing' : 'grab') :
        currentTool === TOOLS.MAIN.INSPECT.id ? 'pointer' :
        currentTool === TOOLS.MAIN.EDIT.id ? (
          editMode === TOOLS.EDIT_SUB.SELECT.id ? 'pointer' :
          editMode === TOOLS.EDIT_SUB.BRUSH.id || editMode === TOOLS.EDIT_SUB.ERASE.id ? 'crosshair' :
          'default'
        ) : 'default';
    }
  }));

  return (
    <>
      {showGrid && gridGeoJSON && (
        <Source 
          key={sourceKey}
          type="geojson" 
          data={gridGeoJSON}
        >
          <Layer {...baseGridLayerStyle} />
          <Layer {...gridLayerStyle} />
          <Layer {...gridOutlineStyle} />
        </Source>
      )}
      
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
              <div className="tool-buttons">
                <button
                  className={`dark-button ${showGrid ? 'active' : ''}`}
                  onClick={toggleGridVisibility}
                >
                  {showGrid ? 'Hide Grid' : 'Show Grid'}
                </button>
                <button
                  className="dark-button warning"
                  onClick={() => {
                    if (window.confirm('Are you sure you want to reset all changes? This action cannot be undone.')) {
                      resetToDefault();
                    }
                  }}
                >
                  Reset All
                </button>
              </div>
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
    </>
  );
});

export default SFProposalVisualizer; 