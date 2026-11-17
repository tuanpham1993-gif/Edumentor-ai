import { useState } from "react";
import LearningPathGraphForDetail from "../components/LearningPathGraphForDetail.jsx";
import LearningPathToolBar from "../components/LearningPathToolBar";
import CourseRecommendation from "../components/CourseRecommendation";
import styles from '../styles/LearningPathDetail.module.css';
import { useLocation, useParams } from "react-router-dom";

export default function LearningPathDetailPage(){
    const location = useLocation()
    const {recordId} = useParams()
    const learningPath = location.state?.learningPath;
    //console.log(learningPath)
    const [selectedSkill, setSelectedSkill] = useState(null)
    if(!learningPath){
        return (
            <main className={styles.detailContainer}>
                <p className={styles.LearningPathEmptyMessage}>
                    Learning path data is unavailable.
                    Please return to My Learning Paths and open it again.   
                </p>
            </main>
        )
    }
    function handleSelectedSkill(skill){
        setSelectedSkill(skill)
    }
    return (
        <main className={styles.detailContainer}>
            {/*Header section*/}
            <header className={styles.detailHeader}>
                <div className={styles.detailTitle}>
                    <h1>{learningPath.original_query}</h1> 
                    <p>Manage your learning path and explore related courses.</p>
                </div>
                <LearningPathToolBar 
                    recordId={Number(recordId)}
                    selectedSkill={selectedSkill}/>
            </header>

            {/*Body section*/}
            <section className={styles.detailContent}>
                <div className={styles.graphSection}>
                    {/*Fix later.......................................*/}
                    <LearningPathGraphForDetail
                        learningPath={learningPath}
                        onSelectSkill={handleSelectedSkill}/>
                </div>

                <aside className={styles.courseSection}>
                    {selectedSkill?(
                        <CourseRecommendation
                            skill={selectedSkill}
                            learningPathId={Number(recordId)}/>
                    ):(
                    <div className={styles.coursePlaceholder}>
                         <div className={styles.placeholderIcon}>
                            <span>↖</span>
                        </div>
                        <h2>Select a skill</h2>
                        <p>
                            Click on any skill in your learning graph
                            to discover recommended courses.
                        </p>
                    </div>)}
                </aside>
            </section>
        </main>
    )
}