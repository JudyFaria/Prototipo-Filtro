import streamlit as st
import pandas as pd

# Dados fictícios
df = pd.DataFrame({
    'A': {
        'Propriedade 1': 5,
        'Propriedade 2': 'sim',
        'Propriedade 3': 100
    },
    'B': {
        'Propriedade 1': 30,
        'Propriedade 2': 'não',
        'Propriedade 3': 90
    },
    'C': {
        'Propriedade 1': 20,
        'Propriedade 2': 'sim',
        'Propriedade 3': 200
    },
    'D': {
        'Propriedade 1': 20,
        'Propriedade 3': 200
    }
})
df = df.T.reset_index().rename(columns={'index': 'Elemento'})

propriedades = df.columns.tolist()[1:]  # exclui 'Elemento'
conectores = ['AND', 'OR']

st.set_page_config(page_title="Filtro Interativo", layout="wide")
st.markdown("<h1 style='text-align: center;'>🔍 Protótipo de Filtro</h1>", unsafe_allow_html=True)

# Estado inicial
if 'filtros' not in st.session_state:
    st.session_state.filtros = []

# --- Função auxiliar para detectar tipo da propriedade
def operadores_disponiveis(nome_prop, tipo, valores_unicos):
    eh_sim_nao = sorted([str(v).lower() for v in valores_unicos]) == ['não', 'sim']
    
    # Força simplificação dos operadores apenas se for "Propriedade 2"
    if nome_prop == "Propriedade 2":
        return ['🟰 IGUAL', '📍 EXISTE'], eh_sim_nao
    else:
        return ['🔼 MAIOR QUE', '🔽 MENOR QUE', '🟰 IGUAL', '📍 EXISTE'], eh_sim_nao
    
# Área de adição de filtro
st.markdown('<div class="fixed-top">', unsafe_allow_html=True)
st.markdown("---")
col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

with col1:
    prop = st.selectbox("🔸 Propriedade", propriedades, key="prop")

tipo = df[prop].dtype
valores_unicos = df[prop].dropna().unique().tolist()
ops_disp, eh_sim_nao = operadores_disponiveis(prop, tipo, valores_unicos)

with col2:
    op = st.selectbox("🔹 Tipo de Condição", ops_disp, key="op")

with col3:
    if 'EXISTE' in op:
        val = ""
        st.text_input("🔘 Valor", value="", key="val", disabled=True)
    else:
        if eh_sim_nao:
            val = st.selectbox("🔘 Valor", ['sim', 'não'], key="val")
        elif pd.api.types.is_numeric_dtype(tipo):
            val = st.number_input("🔘 Valor", key="val", format="%.2f")
        else:
            val = st.text_input("🔘 Valor", key="val")

with col4:
    st.write("")
    if st.button("➕", key="add_filter"):
        st.session_state.filtros.append({
            "prop": prop,
            "op": op,
            "val": val if 'EXISTE' not in op else "",
            "conector": "AND"
        })

# Filtros adicionados
if st.session_state.filtros:
    st.markdown("---")
    st.subheader("🎛️ Condições Aplicadas")

    for i, f in enumerate(st.session_state.filtros):
        if i > 0:
            st.markdown("<div style='text-align:center; margin-bottom:-10px;'>", unsafe_allow_html=True)
            col_con = st.columns([5, 1, 5])
            with col_con[1]:
                st.session_state.filtros[i]['conector'] = st.selectbox(
                    "Conector",
                    conectores,
                    index=conectores.index(f['conector']),
                    key=f"con_{i}",
                    label_visibility="collapsed"
                )
            st.markdown("</div>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

        with col1:
            st.session_state.filtros[i]['prop'] = st.selectbox(
                "", propriedades,
                index=propriedades.index(f['prop']),
                key=f"prop_{i}",
                disabled=True
            )

        prop_i = st.session_state.filtros[i]['prop']
        tipo_i = df[prop_i].dtype
        valores_unicos_i = df[prop_i].dropna().unique().tolist()
        ops_disp_i, eh_sim_nao_i = operadores_disponiveis(prop_i, tipo_i, valores_unicos_i)

        with col2:
            st.session_state.filtros[i]['op'] = st.selectbox(
                "", ops_disp_i,
                index=ops_disp_i.index(f['op']),
                key=f"op_{i}",
                disabled=True
            )

        with col3:
            if 'EXISTE' in st.session_state.filtros[i]['op']:
                st.text_input("", value="", key=f"val_{i}", disabled=True)
                st.session_state.filtros[i]['val'] = ""
            else:
                if eh_sim_nao_i:
                    st.session_state.filtros[i]['val'] = st.selectbox(
                        "", ['sim', 'não'],
                        index=['sim', 'não'].index(f['val']),
                        key=f"val_{i}",
                        disabled=True
                    )
                elif pd.api.types.is_numeric_dtype(tipo_i):
                    st.session_state.filtros[i]['val'] = st.number_input(
                        "", value=float(f['val']) if f['val'] != '' else 0.0,
                        key=f"val_{i}",
                        disabled=True
                    )
                else:
                    st.session_state.filtros[i]['val'] = st.text_input("", value=f['val'], key=f"val_{i}", disabled=True)

        with col4:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.filtros.pop(i)
                st.rerun()

    st.markdown("<div style='text-align:center; margin-top:20px;'>", unsafe_allow_html=True)
    if st.button("🧹 Limpar Tudo"):
        st.session_state.filtros = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Aplicação dos filtros
    resultado = df.copy()
    for i, f in enumerate(st.session_state.filtros):
        prop = f['prop']
        op = f['op']
        val = f['val']

        try:
            if 'EXISTE' in op:
                cond = resultado[prop].notnull()
            elif 'IGUAL' in op:
                cond = resultado[prop].astype(str) == str(val)
            elif 'MAIOR' in op:
                cond = pd.to_numeric(resultado[prop], errors='coerce') > float(val)
            elif 'MENOR' in op:
                cond = pd.to_numeric(resultado[prop], errors='coerce') < float(val)
            else:
                cond = True
        except:
            cond = True

        if i == 0:
            filtro_final = cond
        else:
            if f['conector'] == 'AND':
                filtro_final = filtro_final & cond
            else:
                filtro_final = filtro_final | cond

    st.subheader("🔎 Resultado Filtrado")
    resultado_filtrado = resultado[filtro_final].reset_index(drop=True)
    if resultado_filtrado.empty:
        st.warning("Nenhum elemento corresponde aos critérios selecionados.")
    else:
        st.dataframe(resultado_filtrado)
else:
    st.info("Nenhuma condição adicionada. Adicione filtros para ver os resultados.")
