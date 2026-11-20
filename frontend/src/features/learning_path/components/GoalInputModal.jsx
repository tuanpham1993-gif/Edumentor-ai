import { useEffect, useRef, useState } from "react";
import styles from '../styles/Modal.module.css';
import { createPortal } from 'react-dom';
import { create } from "axios";

export default function GoalInputModal({isOpen, makeItClose, onLoading, isLoading, error}){
    const [goal, setGoal] = useState("")

    useEffect(()=>{
        if(!isOpen || isLoading) return;
        function handleKeyDown(event){
            if (event.key === 'Escape'){
                makeItClose();
            }
        }
        window.addEventListener('keydown', handleKeyDown);
        return () => {
            window.removeEventListener('keydown', handleKeyDown)
        }
    }, [isOpen, makeItClose, isLoading])

    if(!isOpen) return null

    function handleSubmit(event){
        event.preventDefault()
        const trimmedGoal = goal.trim()
        if(!trimmedGoal) return
        onLoading(trimmedGoal)
    }

    function handleClose(){
        if(!isLoading){
            makeItClose();
        }
    }
    return createPortal(
        <div className={styles.backdropModal} onClick={handleClose}>
            <section
            className={styles.modal}
            role="dialog" area-modal="true"
            aria-labelledby="goal-modal-title"
            aria-busy={isLoading}
            onClick={(event)=>event.stopPropagation()}>
                <header className={styles.headerModal}>
                    <h2 id="goal-modal-title">
                        Tạo lộ trình học
                    </h2>
                    <button
                        type="button"
                        className={`${styles.closeButtonModal}`}
                        onClick={handleClose}
                        disabled={isLoading}
                        aria-label="Đóng">
                        &times;
                    </button>
                </header>

                <form onSubmit={handleSubmit}>
                    <div className={styles.bodyModal}>
                        <p className={styles.descriptionModal}>
                            Cho chúng tôi biết bạn muốn học gì.
                            Chúng tôi sẽ giúp bạn xây dựng lộ trình phù hợp.
                        </p>
                        
                        
                        <textarea id="learning-goal"
                        className={styles.textareaModal}
                        placeholder="Ví dụ: Tôi muốn trở thành lập trình viên backend..."
                        value={goal}
                        onChange={(event)=>setGoal(event.target.value)}
                        rows={10} maxLength={2000}
                        disabled={isLoading}/>
                    </div>

                    {error && (
                      <p className={styles.errorMessage} role="alert">
                        {error}
                      </p>  
                    )}

                    {isLoading && (
                        <div
                        className={styles.loadingMessage}
                        role="status"
                        aria-live="polite">
                            <span className={styles.hourglass} aria-hidden="true">⏳</span>
                            <span>Đang tạo lộ trình...</span>
                        </div>
                    )}

                    <footer className={styles.footerModal}>
                        <button type="button"
                        className="btn btn-danger cancelButtonModal"
                        onClick={handleClose}
                        disabled={isLoading}>Cancel
                        </button>

                        <button type="submit"
                        className="btn btn-primary createButtonModal"
                        disabled={!goal.trim() || isLoading}>
                            {isLoading ? "Đang tạo..." : "Tạo lộ trình"}
                        </button>
                    </footer>
                </form>
            </section>
        </div>
    , document.body)
}