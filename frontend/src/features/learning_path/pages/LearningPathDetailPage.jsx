
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";

import LearningPathGraphForDetail from "../components/LearningPathGraphForDetail.jsx";
import LearningPathToolBar from "../components/LearningPathToolBar";
import CourseRecommendation from "../components/CourseRecommendation";

import { getLearningPathById } from "../../../api/learningPaths.api.js";
import styles from "../styles/LearningPathDetail.module.css";

export default function LearningPathDetailPage() {
    const location = useLocation();
    const { recordId } = useParams();

    // Initial data passed from the previous page.
    const initialLearningPath = location.state?.learningPath ?? null;

    // React state: the source of truth for this page.
    const [learningPath, setLearningPath] = useState(initialLearningPath);

    const [selectedSkill, setSelectedSkill] = useState(null);
    const [isLoading, setIsLoading] = useState(!initialLearningPath);
    const [error, setError] = useState("");

    // Fetch data if the user opens the detail page directly
    // or refreshes the browser without navigation state.
    useEffect(() => {
        if (initialLearningPath) return;

        let isMounted = true;

        async function loadLearningPath() {
            try {
                setIsLoading(true);

                const response = await getLearningPathById(recordId);

                if (isMounted) {
                    setLearningPath(response.data);
                }
            } catch (err) {
                if (isMounted) {
                    setError("Không tải được lộ trình này.");
                }
            } finally {
                if (isMounted) {
                    setIsLoading(false);
                }
            }
        }

        loadLearningPath();

        return () => {
            isMounted = false;
        };
    }, [recordId, initialLearningPath]);

    // Called when the user clicks a skill in React Flow.
    function handleSelectedSkill(skill) {
        setSelectedSkill(skill);
    }

    // Refresh the learning path after a successful mutation.
    async function refreshLearningPath() {
        try {
            setError("");

            const response = await getLearningPathById(recordId);
            const updatedLearningPath = response.data;

            // This triggers React to render the updated graph and toolbar.
            setLearningPath(updatedLearningPath);

            // If the selected skill was deleted, clear the selection.
            if (selectedSkill) {
                const selectedId =
                    selectedSkill.skillId ??
                    selectedSkill.skill_id ??
                    selectedSkill.id;

                const stillExists = updatedLearningPath.nodes.some(
                    (node) => node.skill_id === Number(selectedId)
                );

                if (!stillExists) {
                    setSelectedSkill(null);
                }
            }

            return updatedLearningPath;

        } catch (err) {
            console.error("Failed to refresh learning path:", err);
            setError("Không cập nhật được lộ trình.");
            throw err;
        }
    }

    if (isLoading) {
        return (
            <main className={styles.detailContainer}>
                <p>Đang tải lộ trình...</p>
            </main>
        );
    }

    if (!learningPath) {
        return (
            <main className={styles.detailContainer}>
                <p className={styles.LearningPathEmptyMessage}>
                    {error || "Không có dữ liệu lộ trình."}
                     Hãy quay lại Lộ trình của tôi và mở lại.
                </p>
            </main>
        );
    }

    return (
        <main className={styles.detailContainer}>
            {/* Header section */}
            <header className={styles.detailHeader}>
                <div className={styles.detailTitle}>
                    <h1>{learningPath.original_query}</h1>
                    <p>
                        Quản lý lộ trình và khám phá khóa học liên quan.
                    </p>
                </div>

                <LearningPathToolBar
                    recordId={learningPath.record_id}
                    learningPath={learningPath}
                    selectedSkill={selectedSkill}
                    nodes={learningPath.nodes}
                    edges={learningPath.edges}
                    onRefresh={refreshLearningPath}
                />
            </header>

            {error && (
                <p role="alert" className={styles.errorMessage}>
                    {error}
                </p>
            )}

            {/* Body section */}
            <section className={styles.detailContent}>
                <div className={styles.graphSection}>
                    <LearningPathGraphForDetail
                        learningPath={learningPath}
                        onSelectSkill={handleSelectedSkill}
                    />
                </div>

                <aside className={styles.courseSection}>
                    {selectedSkill ? (
                        <CourseRecommendation
                            skill={selectedSkill}
                            learningPathId={Number(recordId)}
                        />
                    ) : (
                        <div className={styles.coursePlaceholder}>
                            <div className={styles.placeholderIcon}>
                                <span>↖</span>
                            </div>

                            <h2>Chọn một kỹ năng</h2>

                            <p>
                                Bấm vào một kỹ năng trên đồ thị
                                để xem khóa học gợi ý.
                            </p>
                        </div>
                    )}
                </aside>
            </section>
        </main>
    );
}
