export const generateRandomPoints = (comments, cityCoords) => {
  const OFFSET = 0.015;
  const defaultOpinions = ['support', 'neutral', 'oppose'];
  
  return comments.map((comment) => {
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
      comment: comment.comment || "No comment provided",
      longitude: cityCoords.longitude + (Math.random() - 0.5) * OFFSET,
      latitude: cityCoords.latitude + (Math.random() - 0.5) * OFFSET,
    };
  });
}; 