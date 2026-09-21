import base64
import os
import tempfile

import streamlit as st

from src.parser import extract_text
from src.jd_extractor import JDExtractor
from src.resume_processor import ResumeProcessor
from src.matching.pipeline import MatchingPipeline


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Resume ↔ JD Semantic Matcher",
    page_icon="🎯",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🎯 Resume ↔ Job Description Semantic Matcher")

st.write(
    "Retrieve, rerank, filter, and explain candidate matches "
    "against a Job Description."
)


# ============================================================
# UPLOAD SECTION
# ============================================================

st.header("Upload Documents")

col1, col2 = st.columns(2)

with col1:

    st.subheader("Job Description")

    jd_file = st.file_uploader(
        "Upload one Job Description",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=False,
        key="jd_upload"
    )

with col2:

    st.subheader("Candidate Resumes")

    resume_files = st.file_uploader(
        "Upload candidate resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key="resume_upload"
    )


# ============================================================
# UPLOAD STATUS
# ============================================================

if jd_file:

    st.success(
        f"JD uploaded: {jd_file.name}"
    )


if resume_files:

    st.success(
        f"{len(resume_files)} candidate resume(s) uploaded."
    )


# ============================================================
# START MATCHING
# ============================================================

if jd_file and resume_files:

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Job Description",
            "1"
        )

    with col2:

        st.metric(
            "Candidates",
            len(resume_files)
        )

    with col3:

        st.metric(
            "Pipeline",
            "Retrieve → Rerank → Filter"
        )


    start_matching = st.button(
        "🚀 Start Matching",
        type="primary",
        use_container_width=True
    )


    if start_matching:

        # ====================================================
        # SAVE JOB DESCRIPTION
        # ====================================================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(
                jd_file.name
            )[1]
        ) as temp_jd:

            temp_jd.write(
                jd_file.getbuffer()
            )

            jd_path = temp_jd.name


        # ====================================================
        # EXTRACT JOB DESCRIPTION TEXT
        # ====================================================

        with st.spinner(
            "Reading Job Description..."
        ):

            jd_text = extract_text(
                jd_path
            )


        # ====================================================
        # STRUCTURE JOB DESCRIPTION
        # ====================================================

        with st.spinner(
            "Extracting job requirements..."
        ):

            jd_extractor = JDExtractor()

            jd_data = jd_extractor.extract(
                jd_text
            )


        # ====================================================
        # SAVE RESUMES
        # ====================================================

        resume_paths = []

        original_filenames = []

        original_file_bytes = {}


        for resume_file in resume_files:

            suffix = os.path.splitext(
                resume_file.name
            )[1]

            file_bytes = (
                resume_file.getvalue()
            )

            temp_resume = (
                tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                )
            )

            temp_resume.write(
                file_bytes
            )

            temp_resume.close()


            resume_paths.append(
                temp_resume.name
            )

            original_filenames.append(
                resume_file.name
            )

            original_file_bytes[
                resume_file.name
            ] = file_bytes


        # ====================================================
        # PROCESS RESUMES
        # ====================================================

        with st.spinner(
            f"Processing {len(resume_paths)} resumes..."
        ):

            processor = ResumeProcessor()

            resumes = processor.process_files(
                resume_paths
            )


        # Restore original filenames

        for resume, original_filename in zip(
            resumes,
            original_filenames
        ):

            resume["filename"] = (
                original_filename
            )


        successful_resumes = [
            resume
            for resume in resumes
            if "error" not in resume
        ]


        failed_resumes = [
            resume
            for resume in resumes
            if "error" in resume
        ]


        if not successful_resumes:

            st.error(
                "No resumes could be processed."
            )

            st.stop()


        # ====================================================
        # COMPLETE MATCHING PIPELINE
        # ====================================================

        with st.spinner(
            "Running semantic retrieval, "
            "Cross-Encoder re-ranking, "
            "structured filtering, "
            "and requirement matching..."
        ):

            pipeline = MatchingPipeline()

            results = pipeline.match(
                jd_text=jd_text,
                jd_data=jd_data,
                resumes=successful_resumes,
                retrieval_top_k=len(
                    successful_resumes
                )
            )


        # ====================================================
        # STORE RESULTS
        # ====================================================

        st.session_state["results"] = results

        st.session_state[
            "original_file_bytes"
        ] = original_file_bytes

        st.session_state[
            "jd_data"
        ] = jd_data

        st.session_state[
            "failed_resumes"
        ] = failed_resumes


        st.success(
            f"Matching completed for "
            f"{len(successful_resumes)} candidate(s)."
        )


# ============================================================
# RESULTS
# ============================================================

if "results" in st.session_state:

    results = st.session_state[
        "results"
    ]

    original_file_bytes = (
        st.session_state.get(
            "original_file_bytes",
            {}
        )
    )

    failed_resumes = (
        st.session_state.get(
            "failed_resumes",
            []
        )
    )


    st.divider()

    st.header(
        "📊 Ranked Candidate Shortlist"
    )


    if failed_resumes:

        st.warning(
            f"{len(failed_resumes)} resume(s) "
            "could not be processed."
        )


    # ========================================================
    # MAIN RANKING TABLE
    # ========================================================

    st.subheader(
        "Candidate Ranking"
    )


    header = st.columns(
        [0.5, 2.2, 1.3, 1.5, 1.2, 1.3]
    )


    with header[0]:

        st.write(
            "**Rank**"
        )


    with header[1]:

        st.write(
            "**Candidate**"
        )


    with header[2]:

        st.write(
            "**Retrieval Score**"
        )


    with header[3]:

        st.write(
            "**Re-ranking Score**"
        )


    with header[4]:

        st.write(
            "**Filter Score**"
        )


    with header[5]:

        st.write(
            "**Final Score**"
        )


    for result in results:

        row = st.columns(
            [0.5, 2.2, 1.3, 1.5, 1.2, 1.3]
        )


        # ----------------------------------------------------
        # RANK
        # ----------------------------------------------------

        with row[0]:

            st.write(
                f"**{result['rank']}**"
            )


        # ----------------------------------------------------
        # CANDIDATE
        # ----------------------------------------------------

        with row[1]:

            st.write(
                f"**{result['filename']}**"
            )


        # ----------------------------------------------------
        # RETRIEVAL
        # ----------------------------------------------------

        with row[2]:

            st.write(
                f"{result['retrieval_score']:.3f}"
            )


        # ----------------------------------------------------
        # RE-RANKING
        # ----------------------------------------------------

        with row[3]:

            st.write(
                f"{result['cross_encoder_score'] * 100:.1f}%"
            )


        # ----------------------------------------------------
        # FILTER
        # ----------------------------------------------------

        with row[4]:

            st.write(
                f"{result['filter_score'] * 100:.1f}%"
            )


        # ----------------------------------------------------
        # FINAL SCORE
        # ----------------------------------------------------

        with row[5]:

            st.write(
                f"**{result['final_score']:.1f}%**"
            )


    # ========================================================
    # DETAILED CANDIDATE VIEW
    # ========================================================

    st.divider()

    st.header(
        "👤 Candidate Analysis"
    )


    for result in results:

        candidate_title = (
            f"#{result['rank']}  |  "
            f"{result['filename']}  |  "
            f"{result['final_score']:.1f}%"
        )


        with st.expander(
            candidate_title
        ):


            # =================================================
            # MATCH SIGNALS
            # =================================================

            st.subheader(
                "Match Signals"
            )


            c1, c2, c3, c4 = st.columns(4)


            with c1:

                st.metric(
                    "Final Score",
                    f"{result['final_score']:.1f}%"
                )


            with c2:

                st.metric(
                    "Retrieval Score",
                    f"{result['retrieval_score']:.3f}"
                )


            with c3:

                st.metric(
                    "Re-ranking Score",
                    f"{result['cross_encoder_score'] * 100:.1f}%"
                )


            with c4:

                st.metric(
                    "Filter Score",
                    f"{result['filter_score'] * 100:.1f}%"
                )


            # =================================================
            # CANDIDATE FIT
            # =================================================

            st.subheader(
                "Candidate Fit"
            )


            c1, c2 = st.columns(2)


            with c1:

                st.metric(
                    "Skill Coverage",
                    f"{result['skill_coverage']:.1f}%"
                )


            with c2:

                experience = result[
                    "experience_match"
                ]

                st.metric(
                    "Experience",
                    experience["status"]
                )


            # =================================================
            # STRUCTURED FILTERS
            # =================================================

            st.subheader(
                "Structured Filters"
            )


            filter_details = result[
                "filter_details"
            ]


            experience_filter = (
                filter_details.get(
                    "experience",
                    {}
                )
            )


            certification_filter = (
                filter_details.get(
                    "certifications",
                    {}
                )
            )


            st.write(
                "**Experience**"
            )


            st.write(
                f"Required: "
                f"{experience_filter.get('required_years')}"
            )


            st.write(
                f"Candidate: "
                f"{experience_filter.get('candidate_years')}"
            )


            st.write(
                f"Status: "
                f"{experience_filter.get('status')}"
            )


            st.write(
                "**Certifications**"
            )


            st.write(
                f"Required: "
                f"{certification_filter.get('required')}"
            )


            st.write(
                f"Candidate: "
                f"{certification_filter.get('candidate')}"
            )


            st.write(
                f"Status: "
                f"{certification_filter.get('status')}"
            )


            # =================================================
            # MATCHED REQUIREMENTS
            # =================================================

            st.subheader(
                "✅ Matched Requirements"
            )


            matched_requirements = (
                result[
                    "matched_requirements"
                ]
            )


            if matched_requirements:

                for item in matched_requirements:

                    st.write(
                        f"✓ **{item['requirement']}**"
                    )


                    st.caption(
                        f"Similarity: "
                        f"{item['similarity']:.3f}"
                    )


                    st.info(
                        f"Evidence: "
                        f"{item['evidence']}"
                    )

            else:

                st.write(
                    "No requirements matched."
                )


            # =================================================
            # UNMATCHED REQUIREMENTS
            # =================================================

            st.subheader(
                "❌ Unmatched Requirements"
            )


            unmatched_requirements = (
                result[
                    "unmatched_requirements"
                ]
            )


            if unmatched_requirements:

                for item in unmatched_requirements:

                    st.write(
                        f"✗ **{item['requirement']}**"
                    )


                    st.caption(
                        f"Best similarity: "
                        f"{item['similarity']:.3f}"
                    )

            else:

                st.write(
                    "No unmatched requirements."
                )


            # =================================================
            # SKILLS
            # =================================================

            st.subheader(
                "🛠 Required Skills"
            )


            skill_col1, skill_col2 = (
                st.columns(2)
            )


            # -------------------------------------------------
            # MATCHED SKILLS
            # -------------------------------------------------

            with skill_col1:

                st.write(
                    "**Matched Skills**"
                )


                matched_skills = (
                    result[
                        "matched_skills"
                    ]
                )


                if matched_skills:

                    for skill in matched_skills:

                        st.write(
                            f"✓ {skill['skill']}"
                        )


                        st.caption(
                            f"Evidence: "
                            f"{skill['evidence']}"
                        )

                else:

                    st.write(
                        "None"
                    )


            # -------------------------------------------------
            # UNMATCHED SKILLS
            # -------------------------------------------------

            with skill_col2:

                st.write(
                    "**Unmatched Skills**"
                )


                unmatched_skills = (
                    result[
                        "unmatched_skills"
                    ]
                )


                if unmatched_skills:

                    for skill in unmatched_skills:

                        st.write(
                            f"✗ {skill['skill']}"
                        )

                else:

                    st.write(
                        "None"
                    )


            # =================================================
            # EXPLANATION
            # =================================================

            st.subheader(
                "🧠 Evidence-Based Explanation"
            )


            st.info(
                result["explanation"]
            )


            # =================================================
            # ORIGINAL RESUME
            # =================================================

            st.subheader(
                "📄 Original Resume"
            )


            filename = result[
                "filename"
            ]


            file_bytes = (
                original_file_bytes.get(
                    filename
                )
            )


            if file_bytes:

                extension = (
                    os.path.splitext(
                        filename
                    )[1]
                    .lower()
                )


                # ------------------------------------------------
                # PDF
                # ------------------------------------------------

                if extension == ".pdf":

                    encoded = (
                        base64.b64encode(
                            file_bytes
                        ).decode()
                    )


                    pdf_data = (
                        "data:application/pdf;base64,"
                        + encoded
                    )


                    st.markdown(
                        f"""
                        <a href="{pdf_data}"
                           target="_blank">
                            <button>
                                📄 Open Original Resume
                            </button>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )


                # ------------------------------------------------
                # DOCX / TXT
                # ------------------------------------------------

                else:

                    st.download_button(
                        label=(
                            "📥 Download Original Resume"
                        ),
                        data=file_bytes,
                        file_name=filename
                    )


# ============================================================
# EMPTY STATE
# ============================================================

else:

    st.info(
        "Upload one Job Description and one or more "
        "candidate resumes to begin."
    )