
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import GoalInputModal from '../components/GoalInputModal'
import { requestLearningPath } from '../../../api/learningPaths.api';
export default function MakeLearningPathPage({onClose}) {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');

  // Called after the user submits a goal.
  async function handleGenerate(goal) {
    setIsGenerating(true);
    setError('');
    try {
      const learningPath = await requestLearningPath({original_query: goal});
      setIsModalOpen(false);
      //console.log(learningPath)
      onClose?.()
      navigate("/me/make-learning-path-generate", {state: {learningPath}})
    } 
    catch (err) {
      setError('Không tạo được lộ trình. Vui lòng thử lại.');
    } 
    finally { 
      setIsGenerating(false); 
    }
  }

  function handleClose() {
    setIsModalOpen(false);
    onClose?.();
  }

  return (
    <div>
      {isModalOpen && (
        <GoalInputModal
          isOpen={isModalOpen}
          makeItClose={handleClose}
          onLoading={handleGenerate}
          isLoading={isGenerating}
          error={error}
        />
      )}
    </div>
  );
}
