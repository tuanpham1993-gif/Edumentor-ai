import { useEffect, useMemo, useState } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';

import ChipMultiSelect from './ChipMultiSelect.jsx';
import SkillProfileEditor from './SkillProfileEditor.jsx';
import { generateLearningPath2, getLearningPathFormOptions } from '../../../api/learningPaths.api.js';
import { CAREER_LEVEL_LABELS } from '../labels.js';
import styles from '../styles/CreatePathModal.module.css';

const EMPTY = {
  original_query: '',
  current_job_title: '',
  career_level: '',
  exp_value: '',
  exp_unit: 'years',
  industry: '',
  technical_domains: [],
  certifications: [],
  skill_profiles: [],
  study_value: '',
  study_unit: 'hours',
  study_period: 'per_week',
  deadline_type: '',
  deadline_date: '',
  deadline_value: '',
  deadline_unit: 'months',
};

const orNull = (s) => (s && s.trim() ? s.trim() : null);

function plural(n, unit) {
  const singular = unit.replace(/s$/, '');
  return `${n} ${Number(n) === 1 ? singular : unit}`;
}

// Form state -> G1Input (backend app/utils/learner_analyzer/schemas.py)
export function toG1Input(f) {
  const study = Number(f.study_value);
  const deadline =
    f.deadline_type === 'fixed_date' && f.deadline_date
      ? { deadline_type: 'fixed_date', target_date: f.deadline_date, duration_value: null, duration_unit: null }
      : f.deadline_type === 'relative_duration' && Number(f.deadline_value) > 0
        ? { deadline_type: 'relative_duration', target_date: null,
            duration_value: Number(f.deadline_value), duration_unit: f.deadline_unit }
        : null;
  return {
    original_query: f.original_query.trim(),
    learner_input: {
      current_job_title: orNull(f.current_job_title),
      career_level: f.career_level || null,
      relevant_it_work_experience: Number(f.exp_value) > 0 ? plural(Number(f.exp_value), f.exp_unit) : null,
      industry: orNull(f.industry),
      technical_domains: f.technical_domains,
      skill_profiles: f.skill_profiles,
      certifications: f.certifications,
      learning_constraints: {
        available_study_time: study > 0 ? { value: study, unit: f.study_unit, period: f.study_period } : null,
        deadline,
      },
    },
  };
}

export default function CreatePathModal({ onClose, initialQuery = '' }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ ...EMPTY, original_query: initialQuery });
  const [options, setOptions] = useState(null);
  const [showMore, setShowMore] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState('');

  useEffect(() => {
    getLearningPathFormOptions()
      .then(setOptions)
      .catch(() => setOptions({ career_levels: Object.keys(CAREER_LEVEL_LABELS), proficiency_levels: [],
                                certifications: [], technical_domains: [] }));
  }, []);

  useEffect(() => {
    if (!isLoading) return undefined;
    setElapsed(0);
    const t = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, [isLoading]);

  useEffect(() => {
    function onKey(e) { if (e.key === 'Escape' && !isLoading) onClose?.(); }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isLoading, onClose]);

  const certOptions = useMemo(() => (options?.certifications ?? [])
    .map((c) => ({ value: c.name, label: c.name, sub: c.issuer ?? undefined })), [options]);
  const domainOptions = useMemo(() => (options?.technical_domains ?? [])
    .map((d) => ({ value: d.name, label: d.name })), [options]);

  const set = (patch) => setForm((f) => ({ ...f, ...patch }));
  const field = (name) => ({ value: form[name], onChange: (e) => set({ [name]: e.target.value }) });

  async function handleSubmit(event) {
    event.preventDefault();
    if (!form.original_query.trim() || isLoading) return;
    setIsLoading(true);
    setError('');
    const request = toG1Input(form);
    try {
      const preview = await generateLearningPath2(request);
      onClose?.();
      navigate('/me/make-learning-path-generate', { state: { preview, request } });
    } catch (err) {
      const status = err.response?.status;
      setError(status === 502
        ? 'Mô hình AI đang bận hoặc trả kết quả lỗi. Vui lòng thử lại sau ít phút.'
        : typeof err.response?.data?.detail === 'string'
          ? err.response.data.detail
          : 'Không tạo được lộ trình. Vui lòng thử lại.');
    } finally {
      setIsLoading(false);
    }
  }

  return createPortal(
    <div className={styles.backdrop} onClick={() => !isLoading && onClose?.()}>
      <section className={styles.modal} role="dialog" aria-modal="true" aria-labelledby="lp2-title"
        aria-busy={isLoading} onClick={(e) => e.stopPropagation()}>
        <header className={styles.header}>
          <div>
            <span className={styles.eyebrow}>✦ Lộ trình AI</span>
            <h2 id="lp2-title">Tạo lộ trình học</h2>
            <p>Mô tả mục tiêu của bạn. Thêm thông tin bên dưới để lộ trình sát với bạn hơn.</p>
          </div>
          <button type="button" className={styles.close} onClick={onClose} disabled={isLoading} aria-label="Đóng">×</button>
        </header>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.body}>
            <label className={styles.label} htmlFor="lp2-query">
              Mục tiêu của bạn <span className={styles.req}>*</span>
            </label>
            <textarea id="lp2-query" className={styles.textarea} rows={5} maxLength={2000} required
              placeholder="Ví dụ: Mình là kế toán 3 năm, biết Excel khá, muốn chuyển sang Data Analyst trong 6 tháng…"
              disabled={isLoading} {...field('original_query')} />
            <div className={styles.counter}>{form.original_query.length}/2000</div>

            <button type="button" className={styles.toggle} onClick={() => setShowMore((v) => !v)}
              aria-expanded={showMore}>
              {showMore ? '▾' : '▸'} Thông tin thêm (không bắt buộc)
            </button>

            {showMore && (
              <fieldset className={styles.more} disabled={isLoading}>
                <div className={styles.grid2}>
                  <div>
                    <label className={styles.label} htmlFor="lp2-job">Công việc hiện tại</label>
                    <input id="lp2-job" className={styles.input} placeholder="vd: Backend developer" maxLength={255}
                      {...field('current_job_title')} />
                  </div>
                  <div>
                    <label className={styles.label} htmlFor="lp2-level">Cấp độ nghề nghiệp</label>
                    <select id="lp2-level" className={styles.select} {...field('career_level')}>
                      <option value="">Chọn cấp độ</option>
                      {(options?.career_levels ?? []).map((c) => (
                        <option key={c} value={c}>{CAREER_LEVEL_LABELS[c] ?? c}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className={styles.label} htmlFor="lp2-exp">Kinh nghiệm làm IT</label>
                    <div className={styles.inline}>
                      <input id="lp2-exp" type="number" min="0" max="50" step="1" className={styles.input}
                        placeholder="0" {...field('exp_value')} />
                      <select className={styles.select} aria-label="Đơn vị kinh nghiệm" {...field('exp_unit')}>
                        <option value="years">năm</option>
                        <option value="months">tháng</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className={styles.label} htmlFor="lp2-industry">Ngành / lĩnh vực</label>
                    <input id="lp2-industry" className={styles.input} placeholder="vd: Tài chính, Y tế…" maxLength={255}
                      {...field('industry')} />
                  </div>
                </div>

                <label className={styles.label}>Mảng kỹ thuật</label>
                <ChipMultiSelect options={domainOptions} value={form.technical_domains}
                  onChange={(v) => set({ technical_domains: v })} placeholder="vd: Backend Development, Data Engineering…" />

                <label className={styles.label}>Kỹ năng bạn đã có</label>
                <SkillProfileEditor rows={form.skill_profiles} onChange={(v) => set({ skill_profiles: v })}
                  proficiencyLevels={options?.proficiency_levels ?? []} />
                <p className={styles.hint}>Kỹ năng “Đã biết” trong Hồ sơ của tôi được tính tự động.</p>

                <label className={styles.label}>Chứng chỉ đang có</label>
                <ChipMultiSelect options={certOptions} value={form.certifications} allowCustom
                  onChange={(v) => set({ certifications: v })} placeholder="vd: AWS Certified Cloud Practitioner…" />

                <div className={styles.grid2}>
                  <div>
                    <label className={styles.label} htmlFor="lp2-study">Thời gian học</label>
                    <div className={styles.inline}>
                      <input id="lp2-study" type="number" min="0" step="0.5" className={styles.input} placeholder="10"
                        {...field('study_value')} />
                      <select className={styles.select} aria-label="Đơn vị" {...field('study_unit')}>
                        <option value="hours">giờ</option>
                        <option value="minutes">phút</option>
                      </select>
                      <select className={styles.select} aria-label="Chu kỳ" {...field('study_period')}>
                        <option value="per_week">/ tuần</option>
                        <option value="per_day">/ ngày</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className={styles.label} htmlFor="lp2-deadline">Hạn hoàn thành</label>
                    <div className={styles.inline}>
                      <select id="lp2-deadline" className={styles.select} {...field('deadline_type')}>
                        <option value="">Không có</option>
                        <option value="relative_duration">Trong khoảng</option>
                        <option value="fixed_date">Đến ngày</option>
                      </select>
                      {form.deadline_type === 'fixed_date' && (
                        <input type="date" className={styles.input} aria-label="Ngày hoàn thành"
                          min={new Date().toISOString().slice(0, 10)} {...field('deadline_date')} />
                      )}
                      {form.deadline_type === 'relative_duration' && (<>
                        <input type="number" min="1" className={styles.input} aria-label="Số lượng" placeholder="6"
                          {...field('deadline_value')} />
                        <select className={styles.select} aria-label="Đơn vị thời gian" {...field('deadline_unit')}>
                          <option value="weeks">tuần</option>
                          <option value="months">tháng</option>
                          <option value="years">năm</option>
                        </select>
                      </>)}
                    </div>
                  </div>
                </div>
              </fieldset>
            )}
          </div>

          {error && <p className={styles.error} role="alert">{error}</p>}

          <footer className={styles.footer}>
            {isLoading ? (
              <div className={styles.loading} role="status" aria-live="polite">
                <span className={styles.spinner} aria-hidden="true" />
                AI đang phân tích hồ sơ và dựng lộ trình… {elapsed}s
              </div>
            ) : <span />}
            <div className={styles.actions}>
              <button type="button" className="btn btn-soft" onClick={onClose} disabled={isLoading}>Hủy</button>
              <button type="submit" className="btn btn-primary" disabled={!form.original_query.trim() || isLoading}>
                {isLoading ? 'Đang tạo…' : 'Tạo lộ trình'}
              </button>
            </div>
          </footer>
        </form>
      </section>
    </div>,
    document.body,
  );
}
