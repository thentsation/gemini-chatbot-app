"""Per-message feedback widget, persisted in st.session_state.feedback_log."""

from datetime import UTC, datetime

import streamlit as st

RATING_OPTIONS = ('Útil', 'Parcialmente útil', 'Não relevante')


def feedback_system(message_index: int) -> None:
    log = st.session_state.setdefault('feedback_log', {})
    existing = log.get(message_index)
    default_index = RATING_OPTIONS.index(existing['rating']) if existing else 0

    rating_col, submit_col = st.columns([3, 1])
    with rating_col:
        rating = st.radio(
            'Como você avalia esta resposta?',
            RATING_OPTIONS,
            index=default_index,
            key=f'feedback_radio_{message_index}',
            horizontal=True,
            label_visibility='collapsed',
        )
    with submit_col:
        if st.button('Enviar', key=f'feedback_submit_{message_index}'):
            existing = log[message_index] = {
                'rating': rating,
                'timestamp': datetime.now(UTC).isoformat(),
            }
            st.toast('Obrigado pelo feedback!')

    if existing:
        st.caption(f'Avaliado como “{existing["rating"]}”')
