import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import LearningPathPreview from '../components/LearningPathPreview';
import LearningPathFeedbackModal from '../components/LearningPathDisagreeFeedback';
import { confirmLearningPath } from '../../../api/learningPaths.api';
import { useAuth } from '../../../hooks/useAuth';

export default function LearningPathPreviewPage() {
    const location = useLocation();
    const navigate = useNavigate();
    const [showFeedback, setShowFeedback] = useState(false);
    const [isConfirming, setIsConfirming] = useState(false);
    const [error, setError] = useState('');
    const learningPath = location.state?.learningPath;
    const {user, status} = useAuth()
    if (!learningPath) {
        return <p>Chưa có dữ liệu lộ trình. Hãy tạo lộ trình trước.</p>;
    }
    function handleCancel() {
        window.scrollTo({
            top: (window.innerHeight / 2 - (window.innerHeight / 2)*10/100),
            behavior: 'smooth'
        });
        setShowFeedback(true);
    }

    async function handleConfirm() {
        if (!learningPath || isConfirming) return;
        if (status !== 'authenticated' || !user) {
            setError('Vui lòng đăng nhập trước khi lưu lộ trình.');
            return;
        }
        setIsConfirming(true);
        setError('');
        console.log(learningPath)
        try {
            const nodes = learningPath.nodes.map((node) => ({
                skill_id: node.skill_id,
                skill_name: node.skill_name,
                node_role: node.node_role,
                is_target: node.is_target ?? false,
                added_by: node.added_by ?? 'system',
                is_required: node.is_required ?? true,
                display_order: node.display_order,
            }));

            const edges = (learningPath.edges ?? []).map((edge) => ({
                from_skill_id: edge.from_skill_id,
                from_skill_name: edge.from_skill_name,
                to_skill_id: edge.to_skill_id,
                to_skill_name: edge.to_skill_name,
                relation_type: edge.relation_type,
            }));

            const payload = {
                confirmed: true,
                original_query: learningPath.original_query,
                goal_type: learningPath.goal_type,
                nodes,
                edges,
                layer: learningPath.layer,
            };
            const response = await confirmLearningPath(payload);
            if (response?.record_id) {
                navigate(`/me/my-learning-path/details/${response.record_id}`, {
                    state: { learningPath: response },
                });
            } else {
                navigate("/me");
            }
        // Future implementation save learning path:
        // fix here
        } catch (err) {
            console.error('Status:', err.response?.status);
            console.error('Validation details:', err.response?.data);
            console.error('Full error:', err);

            setError(
                JSON.stringify(err.response?.data?.detail ?? err.message)
            );
        } finally {
            setIsConfirming(false);
        }
    }
return (<>
    {learningPath && (
        <LearningPathPreview
          learningPath={learningPath}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
          isConfirming={isConfirming}
        />
      )}

    {showFeedback && (
      <LearningPathFeedbackModal onClose={()=>navigate(-1)}/>
    )}
      {error && <p role="alert">{error}</p>}
</>)
}