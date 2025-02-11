import React, { useState, useRef, useCallback } from 'react';
import Map from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { MAPBOX_TOKEN } from '../constants/config';
import SFProposalVisualizer from '../components/SFProposalVisualizer';
import SFAgentVisualizer from '../components/SFAgentVisualizer';
import '../styles/SFAgentVisualizer.css';
import '../styles/SFPage.css';

const SF_COORDINATES = {
  longitude: -122.4194,
  latitude: 37.7749,
  zoom: 12
};

const SFPage = () => {
  const [viewState, setViewState] = useState(SF_COORDINATES);
  const [activeLayer, setActiveLayer] = useState('proposal'); // 'proposal' or 'agents'
  const [map, setMap] = useState(null);
  const [isMapInteractive, setIsMapInteractive] = useState(true);
  const proposalVisualizerRef = useRef(null);

  const onMapLoad = useCallback((event) => {
    setMap(event.target);
  }, []);

  // 处理地图交互状态的回调
  const handleMapInteraction = useCallback((canInteract) => {
    setIsMapInteractive(canInteract);
  }, []);

  // 转发地图事件到 ProposalVisualizer
  const handleMapClick = useCallback((event) => {
    if (activeLayer === 'proposal' && proposalVisualizerRef.current?.handleMapClick) {
      proposalVisualizerRef.current.handleMapClick(event);
    }
  }, [activeLayer]);

  const handleMapMouseDown = useCallback((event) => {
    if (activeLayer === 'proposal' && proposalVisualizerRef.current?.handleMouseDown) {
      proposalVisualizerRef.current.handleMouseDown(event);
    }
  }, [activeLayer]);

  const handleMapMouseUp = useCallback((event) => {
    if (activeLayer === 'proposal' && proposalVisualizerRef.current?.handleMouseUp) {
      proposalVisualizerRef.current.handleMouseUp(event);
    }
  }, [activeLayer]);

  const handleMapMouseMove = useCallback((event) => {
    if (activeLayer === 'proposal' && proposalVisualizerRef.current?.handleMouseMove) {
      proposalVisualizerRef.current.handleMouseMove(event);
    }
  }, [activeLayer]);

  return (
    <div className="sf-page">
      <div className="layer-toggle">
        <button
          className={`toggle-button ${activeLayer === 'proposal' ? 'active' : ''}`}
          onClick={() => setActiveLayer('proposal')}
        >
          Zoning Proposal
        </button>
        <button
          className={`toggle-button ${activeLayer === 'agents' ? 'active' : ''}`}
          onClick={() => setActiveLayer('agents')}
        >
          Resident Feedback
        </button>
      </div>

      <Map
        {...viewState}
        onMove={evt => isMapInteractive && setViewState(evt.viewState)}
        style={{ width: "100%", height: "100vh" }}
        mapStyle="mapbox://styles/mapbox/dark-v10"
        mapboxAccessToken={MAPBOX_TOKEN}
        onLoad={onMapLoad}
        dragPan={isMapInteractive}
        dragRotate={isMapInteractive}
        scrollZoom={isMapInteractive}
        onClick={handleMapClick}
        onMouseDown={handleMapMouseDown}
        onMouseUp={handleMapMouseUp}
        onMouseMove={handleMapMouseMove}
        cursor={proposalVisualizerRef.current?.getCursor?.() || 'default'}
      >
        {map && activeLayer === 'proposal' ? (
          <SFProposalVisualizer 
            ref={proposalVisualizerRef}
            map={map} 
            onMapInteraction={handleMapInteraction}
          />
        ) : map && activeLayer === 'agents' ? (
          <SFAgentVisualizer map={map} />
        ) : null}
      </Map>
    </div>
  );
};

export default SFPage; 