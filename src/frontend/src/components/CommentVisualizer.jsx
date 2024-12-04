import React, { useState, useEffect } from "react";
import Map, { Marker } from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import axios from "axios";
import DetailPanel from "./DetailPanel";
import InfoPanel from './InfoPanel';

const API_URL = "http://localhost:5050";
// const API_URL = "http://172.25.184.18:5050";
const MAPBOX_TOKEN =
  "pk.eyJ1IjoiamFqYW1vYSIsImEiOiJjbDhzeDI4aHgwMXh6M3hrbmVxbG9vcDlyIn0.cdD4-PP7QcxegAsxlhC3mA"; 

const CITY_COORDINATES = {
  boston: { longitude: -71.0589, latitude: 42.3601, zoom: 12 },
  "kendall square": { longitude: -71.0915, latitude: 42.3629, zoom: 15 },
  allston: { longitude: -71.1256, latitude: 42.3539, zoom: 15 },
  "back bay": { longitude: -71.0838, latitude: 42.3503, zoom: 15 },
  brighton: { longitude: -71.1627, latitude: 42.3464, zoom: 15 },
  charlestown: { longitude: -71.0636, latitude: 42.3782, zoom: 15 },
  chinatown: { longitude: -71.0622, latitude: 42.3522, zoom: 15 },
  dorchester: { longitude: -71.0656, latitude: 42.3016, zoom: 15 },
  downtown: { longitude: -71.0589, latitude: 42.3601, zoom: 15 },
  "east boston": { longitude: -71.0124, latitude: 42.3702, zoom: 15 },
  fenway: { longitude: -71.0951, latitude: 42.3458, zoom: 15 },
  "hyde park": { longitude: -71.1245, latitude: 42.2555, zoom: 15 },
  "jamaica plain": { longitude: -71.1117, latitude: 42.3097, zoom: 15 },
  "leather district": { longitude: -71.0578, latitude: 42.3513, zoom: 15 },
  mattapan: { longitude: -71.0922, latitude: 42.2726, zoom: 15 },
  "mission hill": { longitude: -71.1106, latitude: 42.3317, zoom: 15 },
  "north end": { longitude: -71.0542, latitude: 42.3648, zoom: 15 },
  roslindale: { longitude: -71.1305, latitude: 42.2832, zoom: 15 },
  roxbury: { longitude: -71.0846, latitude: 42.3241, zoom: 15 },
  "south boston": { longitude: -71.0502, latitude: 42.3334, zoom: 15 },
  "south end": { longitude: -71.0726, latitude: 42.3389, zoom: 15 },
  "west end": { longitude: -71.0661, latitude: 42.3643, zoom: 15 },
  "west roxbury": { longitude: -71.1587, latitude: 42.2798, zoom: 15 },
  // 可以添加更多社区
};

const CommentVisualizer = () => {
  const [data, setData] = useState(null);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [proposal, setProposal] = useState({
    title: "",
    description: "",
  });
  const [region, setRegion] = useState("boston");
  const [viewState, setViewState] = useState({
    ...CITY_COORDINATES["boston"],
    padding: { top: 0, bottom: 0, left: 0, right: 0 },
  });
  const [isLoading, setIsLoading] = useState(false);
  const [filters, setFilters] = useState({
    age: 'all',
    education: 'all',
    occupation: 'all'
  });

  // 当region改变时更新地图视角
  useEffect(() => {
    const coordinates = CITY_COORDINATES[region.toLowerCase()];
    if (coordinates) {
      setViewState((prev) => ({
        ...prev,
        ...coordinates,
      }));
    }
  }, [region]);

  // 生成随机坐标点（在城市范围内）
  const generateRandomPoints = (comments, cityCoords) => {
    const OFFSET = 0.015;
    const defaultOpinions = ['support', 'neutral', 'oppose'];
    
    return comments.map((comment) => {
      // 如果没有 opinion，随机选择一个
      let normalizedOpinion = comment.opinion ? comment.opinion.toLowerCase() : defaultOpinions[Math.floor(Math.random() * defaultOpinions.length)];
      
      if (normalizedOpinion === 'supports' || normalizedOpinion === 'supporting') {
        normalizedOpinion = 'support';
      } else if (normalizedOpinion === 'opposes' || normalizedOpinion === 'opposing') {
        normalizedOpinion = 'oppose';
      } else if (normalizedOpinion === 'neutral' || normalizedOpinion === 'neither') {
        normalizedOpinion = 'neutral';
      }

      return {
        ...comment,
        opinion: normalizedOpinion,
        comment: comment.comment || "No comment provided", // 如果没有 comment，使用默认值
        longitude: cityCoords.longitude + (Math.random() - 0.5) * OFFSET,
        latitude: cityCoords.latitude + (Math.random() - 0.5) * OFFSET,
      };
    });
  };

  const handleSimulate = async () => {
    setIsLoading(true);
    try {
      const demographicsResponse = await axios.post(
        `${API_URL}/lookup_demographics`,
        null,
        {
          params: { region },
          headers: { "Content-Type": "application/json" },
        }
      );

      if (demographicsResponse.status !== 200) {
        console.error("Error fetching demographics:", demographicsResponse.data);
        return;
      }

      const demographics = demographicsResponse.data.demographics;

      const discussParams = {
        region,
        population: 100000,
        proposal: {
          title: proposal.title,
          description: proposal.description,
        },
        demographics: demographics,
      };

      const discussResponse = await axios.post(
        `${API_URL}/discuss`,
        discussParams,
        {
          headers: { "Content-Type": "application/json" },
        }
      );

      if (discussResponse.status === 200 && discussResponse.data) {
        const cityCoords = CITY_COORDINATES[region.toLowerCase()];
        const comments = discussResponse.data.comments;
        
        // 将对象转换为数组
        const commentsArray = Object.values(comments);
        
        const commentsWithCoordinates = generateRandomPoints(
          commentsArray,
          cityCoords
        );
        
        setData({ 
          ...discussResponse.data, 
          comments: commentsWithCoordinates 
        });
      }
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // 过滤评论
  const filteredComments = data?.comments?.filter(comment => {
    if (!comment.agent) return false;
    
    return (filters.age === 'all' || comment.agent.age === filters.age) &&
           (filters.education === 'all' || comment.agent.education === filters.education) &&
           (filters.occupation === 'all' || comment.agent.occupation === filters.occupation);
  });

  return (
    <div className="visualizer-container">
      <div className="left-panel">
        <h3>Urban Development Proposal</h3>
        <p className="subtitle">Provide details about your proposal</p>
        <select
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          className="dark-input"
        >
          {Object.keys(CITY_COORDINATES).map((city) => (
            <option key={city} value={city}>
              {city.charAt(0).toUpperCase() + city.slice(1)}
            </option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Proposal Title"
          value={proposal.title}
          onChange={(e) =>
            setProposal({ ...proposal, title: e.target.value })
          }
          className="dark-input"
        />
        <textarea
          placeholder="Proposal Description"
          value={proposal.description}
          onChange={(e) =>
            setProposal({ ...proposal, description: e.target.value })
          }
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

export default CommentVisualizer;
