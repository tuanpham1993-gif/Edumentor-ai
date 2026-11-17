
export function getLearningPathSummary(learningPath) {
  const nodes = learningPath.nodes ?? [];
  const completedSkills = nodes.filter((node) => node.is_target === true).length;
  // Prerequisites are included in the total.
  const totalSkills = nodes.length;
  const progressPercentage= totalSkills > 0?
                            Math.round((completedSkills / totalSkills) * 100):0;
  // Completed and abandoned paths keep their backend status.
  let displayStatus;
  if (learningPath.status === 'completed') {
    displayStatus = 'completed';
  } 
  else if (learningPath.status === 'abandoned') {
    displayStatus = 'abandoned';
  } 
  else if (completedSkills > 0) {
    displayStatus = 'ongoing';
  } 
  else {
    displayStatus = 'not_started';
  }

  return {
    completedSkills,
    totalSkills,
    progressPercentage,
    displayStatus,
  };
}
