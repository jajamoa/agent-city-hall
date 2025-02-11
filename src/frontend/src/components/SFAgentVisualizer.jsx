import React, { useState, useEffect } from 'react';
import { Marker, Popup } from 'react-map-gl';
import agentData from '../data/sfAgents.json';

const sentimentColors = {
  positive: '#4CAF50',  // Green
  neutral: '#FFC107',   // Yellow
  negative: '#F44336'   // Red
};

const SFAgentVisualizer = ({ map }) => {
  const [agents, setAgents] = useState(agentData.agents);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [filters, setFilters] = useState({
    sentiment: 'all',
    neighborhood: 'all',
    reasons: []
  });

  // Get all possible reasons
  const allReasons = [...new Set(agents.flatMap(agent => agent.reasons))];
  
  // Get all possible neighborhoods
  const allNeighborhoods = [...new Set(agents.map(agent => agent.neighborhood))];

  // Filter agents
  const filteredAgents = agents.filter(agent => {
    const sentimentMatch = filters.sentiment === 'all' || agent.sentiment === filters.sentiment;
    const neighborhoodMatch = filters.neighborhood === 'all' || agent.neighborhood === filters.neighborhood;
    const reasonsMatch = filters.reasons.length === 0 || 
      agent.reasons.some(reason => filters.reasons.includes(reason));
    
    return sentimentMatch && neighborhoodMatch && (filters.reasons.length === 0 || reasonsMatch);
  });

  // Handle filter changes
  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  // Handle reason filter changes
  const handleReasonToggle = (reason) => {
    setFilters(prev => ({
      ...prev,
      reasons: prev.reasons.includes(reason)
        ? prev.reasons.filter(c => c !== reason)
        : [...prev.reasons, reason]
    }));
  };

  return (
    <>
      {/* Agents on Map */}
      {filteredAgents.map(agent => (
        <Marker
          key={agent.id}
          longitude={agent.location.longitude}
          latitude={agent.location.latitude}
          anchor="center"
          onClick={e => {
            e.originalEvent.stopPropagation();
            setSelectedAgent(agent);
          }}
        >
          <div
            className={`agent-marker ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
            style={{
              backgroundColor: sentimentColors[agent.sentiment],
              boxShadow: `0 0 8px ${sentimentColors[agent.sentiment]}80`
            }}
          />
        </Marker>
      ))}

      {/* Agent Popup */}
      {selectedAgent && (
        <Popup
          longitude={selectedAgent.location.longitude}
          latitude={selectedAgent.location.latitude}
          anchor="top"
          onClose={() => setSelectedAgent(null)}
          closeOnClick={false}
        >
          <div className="agent-popup">
            <h3>{selectedAgent.name}</h3>
            <p>{selectedAgent.occupation}</p>
            <p>{selectedAgent.comment}</p>
          </div>
        </Popup>
      )}

      {/* Filter Panel */}
      <div className="filter-panel dark-theme">
        <div className="toolbar-header">
          <h3>Resident Filters</h3>
        </div>
        
        <div className="toolbar-content">
          <div className="tool-section">
            <div className="tool-label">Sentiment</div>
            <select
              value={filters.sentiment}
              onChange={(e) => handleFilterChange('sentiment', e.target.value)}
              className="dark-select"
            >
              <option value="all">All</option>
              <option value="positive">Support</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Oppose</option>
            </select>
          </div>

          <div className="tool-section">
            <div className="tool-label">Neighborhood</div>
            <select
              value={filters.neighborhood}
              onChange={(e) => handleFilterChange('neighborhood', e.target.value)}
              className="dark-select"
            >
              <option value="all">All</option>
              {allNeighborhoods.map(neighborhood => (
                <option key={neighborhood} value={neighborhood}>
                  {neighborhood}
                </option>
              ))}
            </select>
          </div>

          <div className="tool-section">
            <div className="tool-label">Reasons</div>
            <div className="reasons-container">
              {allReasons.map(reason => (
                <label key={reason} className="reason-checkbox">
                  <input
                    type="checkbox"
                    checked={filters.reasons.includes(reason)}
                    onChange={() => handleReasonToggle(reason)}
                  />
                  {reason}
                </label>
              ))}
            </div>
          </div>

          <div className="tool-section">
            <div className="tool-label">Statistics</div>
            <p>Showing Residents: {filteredAgents.length}</p>
            <div className="sentiment-distribution">
              <div className="sentiment-bar">
                <div
                  className="sentiment-positive"
                  style={{
                    width: `${(filteredAgents.filter(a => a.sentiment === 'positive').length / filteredAgents.length) * 100}%`,
                    backgroundColor: sentimentColors.positive
                  }}
                />
                <div
                  className="sentiment-neutral"
                  style={{
                    width: `${(filteredAgents.filter(a => a.sentiment === 'neutral').length / filteredAgents.length) * 100}%`,
                    backgroundColor: sentimentColors.neutral
                  }}
                />
                <div
                  className="sentiment-negative"
                  style={{
                    width: `${(filteredAgents.filter(a => a.sentiment === 'negative').length / filteredAgents.length) * 100}%`,
                    backgroundColor: sentimentColors.negative
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Details Panel */}
      {selectedAgent && (
        <div className="agent-details-panel dark-theme">
          <div className="toolbar-header">
            <h3>{selectedAgent.name}</h3>
            <button className="close-button" onClick={() => setSelectedAgent(null)}>×</button>
          </div>
          
          <div className="toolbar-content">
            <div className="detail-row">
              <span className="detail-label">Age:</span>
              <span>{selectedAgent.age}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Occupation:</span>
              <span>{selectedAgent.occupation}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Neighborhood:</span>
              <span>{selectedAgent.neighborhood}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Sentiment:</span>
              <span style={{ color: sentimentColors[selectedAgent.sentiment] }}>
                {selectedAgent.sentiment === 'positive' ? 'Support' :
                 selectedAgent.sentiment === 'neutral' ? 'Neutral' : 'Oppose'}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Reasons:</span>
              <div className="reasons-tags">
                {selectedAgent.reasons.map(reason => (
                  <span key={reason} className="reason-tag">{reason}</span>
                ))}
              </div>
            </div>
            <div className="detail-row">
              <span className="detail-label">Comment:</span>
              <p className="agent-comment">{selectedAgent.comment}</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default SFAgentVisualizer; 