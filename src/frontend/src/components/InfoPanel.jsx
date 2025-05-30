import React from 'react';

const InfoPanel = ({ data, selectedPoint, filters, setFilters }) => {
  // 格式化字符串：去掉下划线并将首字母大写
  const formatString = (str) => {
    return str.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  // 过滤评论
  const filteredComments = data?.comments?.filter(comment => {
    if (!comment.agent) return false;
    
    return (filters.age === 'all' || comment.agent.age === filters.age) &&
           (filters.education === 'all' || comment.agent.education === filters.education) &&
           (filters.occupation === 'all' || comment.agent.occupation === filters.occupation);
  });

  // 计算筛选后的统计数据
  const getFilteredStats = () => {
    if (!filteredComments) return null;
    
    const stats = {
      support: 0,
      neutral: 0,
      oppose: 0
    };

    filteredComments.forEach(comment => {
      stats[comment.opinion]++;
    });

    const total = filteredComments.length;
    return {
      support: total ? (stats.support / total) * 100 : 0,
      neutral: total ? (stats.neutral / total) * 100 : 0,
      oppose: total ? (stats.oppose / total) * 100 : 0
    };
  };

  const stats = getFilteredStats();

  // 获取所有唯一的选项值
  const getUniqueOptions = (field) => {
    if (!data?.comments) return [];
    const uniqueValues = new Set(
      data.comments
        .filter(comment => comment.agent && comment.agent[field])
        .map(comment => comment.agent[field])
    );
    return Array.from(uniqueValues).sort();
  };

  // 获取每个筛选器的选项
  const ageOptions = getUniqueOptions('age');
  const educationOptions = getUniqueOptions('education');
  const occupationOptions = getUniqueOptions('occupation');

  return (
    <div className="info-panel">
      {/* Demographic Filters */}
      <div className="panel-section">
        <h3>Demographic Filters</h3>
        <div className="filter-group">
          <select 
            className="dark-input"
            value={filters.age}
            onChange={(e) => setFilters({...filters, age: e.target.value})}
          >
            <option value="all">All Ages</option>
            {ageOptions.map(age => (
              <option key={age} value={age}>{age}</option>
            ))}
          </select>

          <select 
            className="dark-input"
            value={filters.education}
            onChange={(e) => setFilters({...filters, education: e.target.value})}
          >
            <option value="all">All Education Levels</option>
            {educationOptions.map(education => (
              <option key={education} value={education}>
                {formatString(education)}
              </option>
            ))}
          </select>

          <select 
            className="dark-input"
            value={filters.occupation}
            onChange={(e) => setFilters({...filters, occupation: e.target.value})}
          >
            <option value="all">All Occupations</option>
            {occupationOptions.map(occupation => (
              <option key={occupation} value={occupation}>
                {formatString(occupation)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="panel-section">
          <h3>Statistics</h3>
          <div className="stats-bars">
            <div className="stat-item">
              <div className="stat-label">Support</div>
              <div className="stat-bar-container">
                <div 
                  className="stat-bar support"
                  style={{width: `${stats.support}%`}}
                />
                <span className="stat-value">{stats.support.toFixed(1)}%</span>
              </div>
            </div>
            <div className="stat-item">
              <div className="stat-label">Neutral</div>
              <div className="stat-bar-container">
                <div 
                  className="stat-bar neutral"
                  style={{width: `${stats.neutral}%`}}
                />
                <span className="stat-value">{stats.neutral.toFixed(1)}%</span>
              </div>
            </div>
            <div className="stat-item">
              <div className="stat-label">Oppose</div>
              <div className="stat-bar-container">
                <div 
                  className="stat-bar oppose"
                  style={{width: `${stats.oppose}%`}}
                />
                <span className="stat-value">{stats.oppose.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Agent Details */}
      {selectedPoint && (
        <div className="panel-section">
          <h3>Agent Details</h3>
          <div className="comment-details">
            <div className="agent-info">
              {/* Agent Name Row */}
              <div className="agent-name-row">
                <span className="label">Agent Name:</span>
                <span className="agent-id">
                  {`0x${selectedPoint.id.toString().padStart(2, '0')}`}
                </span>
              </div>

              {/* Opinion Row */}
              <div className="opinion-info">
                <span className="label">Opinion</span>
                <span className={`opinion-tag ${selectedPoint.opinion}`}>
                  {selectedPoint.opinion}
                </span>
              </div>

              {/* Demographics Section */}
              <div className="demographics-section">
                <div className="demographics-title">Demographics</div>
                <div className="agent-details">
                  <div>Age: {selectedPoint.agent?.age || 'N/A'}</div>
                  <div>Education: {formatString(selectedPoint.agent?.education || 'N/A')}</div>
                  <div>Occupation: {formatString(selectedPoint.agent?.occupation || 'N/A')}</div>
                </div>
              </div>

              {/* Comment Section */}
              <div className="comment-section">
                <span className="label">Comment</span>
                <div className="comment-text">
                  {selectedPoint.comment}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InfoPanel; 