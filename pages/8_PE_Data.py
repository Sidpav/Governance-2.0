import streamlit as st

from ui.theme import apply_theme
from ui.sidebar import render_sidebar
from ui.navbar import render_navbar, render_breadcrumb
from ui.auth import require_login, require_access

from llm.data_generator import generate_data_requirements

from database.project_execution_repository import (
    get_approved_projects,
    load_hypotheses,
)
from database.project_execution_repository import (
    load_experiments,
    load_prototype_spec,
)

from database.data_repository import (
    load_data_requirements,
    save_data_requirements,
    load_data_review,
    update_attribute,
    update_leakage_answer,
    update_quality_answer,
    update_source_trust,
    update_topic,
    load_model_requirements,
    save_model_requirements,
)

from llm.model_requirement_generator import (
    generate_model_requirements,
)

st.set_page_config(
    page_title="AI Product Delivery - Data",
    page_icon="🗄️",
    layout="wide",
)

require_login()

if "show_requirements" not in st.session_state:

    st.session_state.show_requirements = False

apply_theme()

render_sidebar(active="pe_data")

render_navbar(active="pe_data")

require_access("pe_data")

render_breadcrumb(
    "AI Product Delivery",
    "Data",
)

st.title("🗄️ Data")

st.caption(
    "Review data requirements for the project."
)

st.divider()

projects = get_approved_projects()

if not projects:

    st.warning("No approved projects found.")

    st.stop()

project_map = {

    f"{p['id']} - {p['problem_statement']}": p

    for p in projects

}

selected = st.selectbox(

    "Select Project",

    list(project_map.keys()),

    width="stretch",

)

project = project_map[selected]

prototype_spec = load_prototype_spec(
    project["id"]
)

if not prototype_spec:

    st.warning(
        "Prototype Specification has not been generated yet."
    )

    st.stop()

hypotheses = [

    h

    for h in load_hypotheses(project["id"])

    if h.get("status") == "Approved"

]

experiments = load_experiments(
    project["id"]
)

approved_experiments = [

    e

    for e in experiments

    if e.get("status") == "Approved"

]

requirements = load_data_requirements(
    project["id"]
)

if requirements is None:

    with st.spinner(
        "Generating Data Requirements..."
    ):

        requirements = generate_data_requirements(

            project,

            hypotheses,

            approved_experiments,

            prototype_spec,

        )

        save_data_requirements(

            project["id"],

            requirements,

        )

        st.rerun()

if not requirements:

    st.error(
        "Unable to generate data requirements."
    )

    st.stop()

review = load_data_review(
    project["id"]
)

if "data_step" not in st.session_state:

    st.session_state.data_step = 1

step = st.session_state.data_step

if step == 1:

    st.header("📊 Required Structured Data")

    st.caption(
        "The following structured datasets have been identified for this project."
    )

    st.divider()

    for group in requirements["structured_data"]:

        with st.container(border=True):

            st.markdown(
                f"## {group['group']}"
            )

            st.divider()

            for category in group["categories"]:

                st.subheader(category["name"])

                header = st.columns([5,2,4])

                header[0].markdown("**Attribute**")
                header[1].markdown("**Available**")
                header[2].markdown("**Missing Data %**")

                for attribute in category["attributes"]:

                    row = st.columns(
                        [5, 2, 4]
                    )

                    with row[0]:

                        st.write(attribute)

                    with row[1]:

                        attribute_id = (
                            f"{group['group']}|"
                            f"{category['name']}|"
                            f"{attribute}"
                        )

                        attribute_review = review.get(
                            "attributes",
                            {}
                        ).get(
                            attribute_id,
                            {}
                        )

                        available = st.checkbox(

                            "Available",

                            value=attribute_review.get(
                                "available",
                                False,
                            ),

                            key=f"{group['group']}_{category['name']}_{attribute}_available",

                        )

                    with row[2]:

                        missing = st.slider(

                            "Missing Data %",

                            0,

                            100,

                            attribute_review.get(
                                "missing_percent",
                                0,
                            ),

                            disabled=not available,

                            key=f"{group['group']}_{category['name']}_{attribute}_missing",
                        )
                        
                    update_attribute(

                        project["id"],

                        attribute,

                        available,

                        missing,

                    )

    st.divider()

    st.subheader("Data Leakage Assessment")

    header = st.columns([7, 2])

    header[0].markdown("**Question**")
    header[1].markdown("**Answer**")

    for i, question in enumerate(
        requirements["data_leakage_questions"]
    ):

        row = st.columns([7, 2])

        with row[0]:

            st.write(question)

        with row[1]:

            answer = st.selectbox(

                "Answer",

                [

                    "Yes",

                    "No",

                    "Partial",

                ],

                key=f"leak_{i}",

                label_visibility="collapsed",

            )

        update_leakage_answer(

            project["id"],

            question,

            answer,

        )

    st.divider()

    st.subheader("Data Quality & Consistency")

    header = st.columns([7, 2])

    header[0].markdown("**Question**")
    header[1].markdown("**Answer**")

    for i, question in enumerate(
        requirements["data_quality_questions"]
    ):

        row = st.columns([7, 2])

        with row[0]:

            st.write(question)

        with row[1]:

            answer = st.selectbox(

                "Answer",

                [

                    "Yes",

                    "No",

                    "Partial",

                ],

                key=f"quality_{i}",

                label_visibility="collapsed",

            )

        update_quality_answer(

            project["id"],

            question,

            answer,

        )

    st.divider()

    _, right = st.columns([6, 2])

    with right:

        if st.button(

            "Proceed to Unstructured Data →",

            width='stretch',

        ):

            st.session_state.data_step = 2

            st.rerun()

elif step == 2:

    st.header("📄 Required Unstructured Data")

    st.caption(
        "Review required unstructured data sources."
    )

    st.divider()

    for group in requirements["unstructured_data"]:

        with st.container(border=True):

            st.markdown(
                f"## {group['group']}"
            )

            st.divider()

            for category in group["categories"]:

                st.subheader(category["name"])

                header = st.columns([5,3,3])

                header[0].markdown("**Source**")
                header[1].markdown("**Category**")
                header[2].markdown("**Trustworthiness**")

                for source in category["sources"]:

                    row = st.columns([5,3,3])

                    with row[0]:

                        st.write(source)

                    with row[1]:

                        st.write(category["name"])

                    with row[2]:

                        options = [

                            "Human",

                            "System",

                            "Partial",

                            "Mixed",

                            "Subjective",

                            "Standardized",

                            "Yes",

                            "No",

                        ]

                        saved = review.get(
                            "trustworthiness",
                            {}
                        ).get(
                            f"{group['group']}|{category['name']}|{source}",
                            options[0],
                        )

                        trust = st.selectbox(

                            "Trustworthiness",

                            options,

                            index=options.index(saved),

                            label_visibility="collapsed",

                            key=f"{group['group']}_{category['name']}_{source}_trust",

                        )

                        update_source_trust(

                            project["id"],

                            f"{group['group']}|{category['name']}|{source}",

                            trust,

                        )

                st.divider()

    st.divider()

    if st.button(

        "Requirements Review",

        type="primary",

        width='stretch',

    ):

        models = load_model_requirements(
            project["id"]
        )

        if models is None:

            with st.spinner(
                "Generating AI / Model Requirements..."
            ):

                models = generate_model_requirements(

                    project,

                    prototype_spec,

                    requirements,

                )

                save_model_requirements(

                    project["id"],

                    models,

                )

        st.session_state.show_requirements = True

        st.rerun()

    if st.session_state.show_requirements:

        models = load_model_requirements(
            project["id"]
        )

        if models:

            st.divider()

            st.header(
                "🤖 AI / LLM / Model Requirements"
            )

            for model in models["models"]:

                with st.container(border=True):

                    st.subheader(
                        model["name"]
                    )

                    st.caption(
                        model["type"]
                    )

                    st.write(
                        model["reason"]
                    )

    st.divider()

    st.header("📚 Topic Coverage Check")

    covered = 0

    for topic in requirements["topic_coverage"]:

        topic_id = f"topic_{topic}"

        current = review.get(
            "topics",
            {}
        ).get(
            topic,
            "Not Covered",
        )

        if current == "Not Covered":
            color = "⚪"
        elif current == "Partially Covered":
            color = "🟡"
        else:
            color = "🟢"
            covered += 1

        col1, col2 = st.columns([3,7])

        with col1:

            if st.button(

                f"{color} {topic}",

                key=topic_id,

            ):

                if current == "Not Covered":

                    new = "Partially Covered"

                elif current == "Partially Covered":

                    new = "Well Covered"

                else:

                    new = "Not Covered"

                update_topic(

                    project["id"],

                    topic,

                    new,

                )

                st.rerun()

    st.caption(
        f"{covered}/{len(requirements['topic_coverage'])} topics adequately covered"
    )

    st.divider()

    _, right = st.columns([6,1])

    with right:

        if st.button(

            "Proceed to Infrastructure →",

            width='stretch',

        ):

            st.switch_page(
                "pages/9_PE_Infrastructure.py"
            )
