import React, { useState, useEffect } from "react";
import Map, { Marker } from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import DetailPanel from "./DetailPanel";
import InfoPanel from './InfoPanel';
import { MAPBOX_TOKEN, CITY_COORDINATES } from '../constants/config';
import { generateRandomPoints } from '../utils/mapUtils';
import { api } from '../services/api';

const BostonProposalVisualizer = () => {
  const [data, setData] = useState(null);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [proposal, setProposal] = useState({
    title: "",
    description: "",
  });
  const [region, setRegion] = useState('boston');
  const [viewState, setViewState] = useState({
    ...CITY_COORDINATES['boston'],
    padding: { top: 0, bottom: 0, left: 0, right: 0 },
  });
  const [isLoading, setIsLoading] = useState(false);
  const [filters, setFilters] = useState({
    age: 'all',
    education: 'all',
    occupation: 'all'
  });

  useEffect(() => {
    const coordinates = CITY_COORDINATES[region.toLowerCase()];
    if (coordinates) {
      setViewState((prev) => ({
        ...prev,
        ...coordinates,
      }));
    }
  }, [region]);

  const handleSimulate = async () => {
    setIsLoading(true);
    try {
      const { demographics } = await api.lookupDemographics(region);

      const discussParams = {
        region,
        population: 100000,
        proposal: {
          title: proposal.title,
          description: proposal.description,
        },
        demographics: demographics,
      };

      const discussResponse = await api.discuss(discussParams);
      const comments = discussResponse.comments;
      
      const commentsArray = Object.values(comments);
      const commentsWithCoordinates = generateRandomPoints(
        commentsArray,
        CITY_COORDINATES[region.toLowerCase()]
      );
      
      setData({ 
        ...discussResponse, 
        comments: commentsWithCoordinates 
      });
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredComments = data?.comments?.filter(comment => {
    if (!comment.agent) return false;
    
    return (filters.age === 'all' || comment.agent.age === filters.age) &&
           (filters.education === 'all' || comment.agent.education === filters.education) &&
           (filters.occupation === 'all' || comment.agent.occupation === filters.occupation);
  });

  return (
    <div className="visualizer-container">
      <div className="left-panel">
        <h3>Boston Urban Development Proposal</h3>
        <p className="subtitle">Provide details about your proposal</p>
        <select
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          className="dark-input"
        >
          {Object.keys(CITY_COORDINATES)
            .filter(city => city.includes('boston') || 
                          ['allston', 'brighton', 'charlestown', 'dorchester', 
                           'fenway', 'roxbury', 'downtown'].includes(city))
            .map((city) => (
              <option key={city} value={city}>
                {city.charAt(0).toUpperCase() + city.slice(1)}
              </option>
            ))}
        </select>
        <input
          type="text"
          placeholder="Proposal Title"
          value={proposal.title}
          onChange={(e) => setProposal({ ...proposal, title: e.target.value })}
          className="dark-input"
        />
        <textarea
          placeholder="Proposal Description"
          value={proposal.description}
          onChange={(e) => setProposal({ ...proposal, description: e.target.value })}
          className="dark-input description-box"
        />
        <button
          onClick={handleSimulate}
          className={`dark-button ${isLoading ? "loading" : ""}`}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <div className="spinner">
                <div className="spinner-inner"></div>
              </div>
              Loading
            </>
          ) : (
            "Simulate"
          )}
        </button>
      </div>

      <div className="main-content">
        <Map
          {...viewState}
          onMove={(evt) => setViewState(evt.viewState)}
          style={{ width: "100%", height: "100%" }}
          mapStyle="mapbox://styles/mapbox/dark-v10"
          mapboxAccessToken={MAPBOX_TOKEN}
        >
          {filteredComments?.map((comment, index) => (
            <Marker
              key={index}
              longitude={comment.longitude}
              latitude={comment.latitude}
              onClick={() => setSelectedPoint(comment)}
            >
              <div className={`marker ${comment.opinion} ${selectedPoint?.id === comment.id ? 'selected' : ''}`} />
            </Marker>
          ))}
        </Map>
      </div>

      <InfoPanel data={data} selectedPoint={selectedPoint} filters={filters} setFilters={setFilters} />
    </div>
  );
};

export default BostonProposalVisualizer; 