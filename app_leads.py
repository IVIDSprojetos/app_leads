import streamlit as st
import time
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Jaú Imóvel Na Mão",
    page_icon="🏠",
    layout="centered"
)

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 3em;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .hero-section {
        background-color: #111827;
        padding: 60px 20px;
        border-radius: 25px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&q=80&w=1200');
        background-size: cover;
        background-position: center;
    }
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #f1f3f5;
        margin-bottom: 20px;
    }
    .property-price {
        color: #2563eb;
        font-size: 1.5rem;
        font-weight: 900;
    }
    .badge {
        background-color: #eff6ff;
        color: #2563eb;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA CONEXÃO SQLITE ---
# O Streamlit usa st.connection para gerenciar conexões com bancos de dados.
# No segredo ou configuração, o tipo 'sqlite' será identificado.
conn = st.connection("imoveis_db", type="sql", url="sqlite:///imoveis.db")

# --- DADOS MOCK ---
ESTADOS_BR = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]

# --- INICIALIZAÇÃO DO ESTADO ---
if 'view' not in st.session_state:
    st.session_state.view = 'home'
if 'quiz_step' not in st.session_state:
    st.session_state.quiz_step = 0
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = {}
if 'form_data' not in st.session_state:
    st.session_state.form_data = {"name": "", "email": "", "phone": ""}
if 'search_results' not in st.session_state:
    st.session_state.search_results = None

# --- PERGUNTAS DO QUIZ ---
questions = [
    { 
        "id": 'property_type', 
        "title": "O que você está buscando em Jaú?", 
        "type": 'buttons',
        "options": ["Casa", "Apartamento", "Terreno", "Condomínios Rurais", "Chácara", "Sobrado"] 
    },
    { 
        "id": 'age_range', 
        "title": "Qual a sua faixa etária?", 
        "type": 'buttons',
        "options": ["18 a 30 anos", "31 a 50 anos", "Acima de 50 anos"] 
    },
    { 
        "id": 'state', 
        "title": "Em que estado reside atualmente?", 
        "type": 'dropdown'
    },
    { 
        "id": 'neighborhood_preference', 
        "title": "Onde se imagina a viver em Jaú?", 
        "type": 'buttons',
        "options": ["Perto do comércio", "Bairros residenciais", "Áreas de expansão", "Saída para Rodovia"] 
    }
]

# --- FUNÇÕES DE NAVEGAÇÃO ---
def set_view(view_name):
    st.session_state.view = view_name
    st.rerun()

def next_step(answer):
    current_q = questions[st.session_state.quiz_step]
    st.session_state.quiz_data[current_q['id']] = answer
    
    if st.session_state.quiz_step < len(questions) - 1:
        st.session_state.quiz_step += 1
    else:
        st.session_state.view = 'contact_form'
    st.rerun()

def prev_step():
    if st.session_state.quiz_step > 0:
        st.session_state.quiz_step -= 1
    else:
        st.session_state.view = 'home'
    st.rerun()

# --- FUNÇÕES DE CONSULTA AO BANCO ---
def search_properties_db(quiz_data: dict):
    try:
        property_type = quiz_data.get('property_type', '')
        
        # Query SQL usando o padrão st.connection (SQLAlchemy por baixo)
        # O parâmetro params ajuda a prevenir SQL Injection
        query = "SELECT * FROM properties WHERE type LIKE :prop_type ORDER BY price DESC LIMIT 50"
        
        # Executa a query e retorna um DataFrame
        df = conn.query(query, params={"prop_type": f"%{property_type}%"}, ttl=600)
        
        if not df.empty:
            # Converte DataFrame para lista de dicionários para manter compatibilidade com o resto do código
            properties = df.to_dict('records')
            return {
                "total_results": len(properties),
                "properties": properties
            }
        else:
            return {"total_results": 0, "properties": []}
            
    except Exception as e:
        st.error(f"❌ Erro ao buscar imóveis no banco: {str(e)}")
        return None

# --- INTERFACE ---

# Navbar Simples
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🏠 JAÚ IMÓVEL", key="nav_home"):
        st.session_state.view = 'home'
        st.session_state.quiz_step = 0
        st.rerun()

# Conteúdo Principal
if st.session_state.view == 'home':
    st.markdown("""
        <div class="hero-section">
            <h1 style='font-size: 3.5rem; font-weight: 900; margin-bottom: 10px;'>IMÓVEL NA MÃO <span style='color: #3b82f6; font-style: italic;'>JAÚ</span></h1>
            <p style='font-size: 1.2rem; opacity: 0.9; margin-bottom: 30px;'>Todos os imóveis da cidade agregados em um só lugar.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Começar Pesquisa Inteligente", type="primary", use_container_width=True):
        set_view('quiz')

elif st.session_state.view == 'quiz':
    step = st.session_state.quiz_step
    q = questions[step]
    
    # Progresso
    progress = (step + 1) / (len(questions) + 1)
    st.progress(progress)
    
    col_back, col_step = st.columns([1, 1])
    with col_back:
        if st.button("← Voltar", key="back_btn"):
            prev_step()
    with col_step:
        st.markdown(f"<p style='text-align: right; color: #2563eb; font-weight: bold; font-size: 0.8rem;'>ETAPA {step + 1} DE {len(questions) + 1}</p>", unsafe_allow_html=True)

    st.markdown(f"<h2 style='font-size: 2.5rem; font-weight: 900; margin: 40px 0;'>{q['title']}</h2>", unsafe_allow_html=True)

    if q['type'] == 'buttons':
        cols = st.columns(2)
        for i, opt in enumerate(q['options']):
            if cols[i % 2].button(opt, key=f"opt_{i}", use_container_width=True):
                next_step(opt)
    
    elif q['type'] == 'dropdown':
        selected_state = st.selectbox("Selecione o Estado", [""] + ESTADOS_BR)
        if selected_state:
            if st.button("Continuar", type="primary"):
                next_step(selected_state)

elif st.session_state.view == 'contact_form':
    st.markdown("<h2 style='font-size: 2rem; font-weight: 900; text-transform: uppercase;'>Falta pouco!</h2>", unsafe_allow_html=True)
    st.write("Confirme seus dados para processarmos os resultados dos portais de Jaú.")
    
    with st.form("contact_form"):
        name = st.text_input("Nome Completo *", placeholder="Ex: João Silva")
        email = st.text_input("E-mail Corporativo ou Pessoal *", placeholder="seu@email.com")
        phone = st.text_input("Whatsapp", placeholder="(14) 99999-9999")
        
        submit = st.form_submit_button("VER RESULTADOS NOS SITES", use_container_width=True)
        if submit:
            if not name or not email:
                st.error("Por favor, preencha os campos obrigatórios.")
            else:
                st.session_state.form_data = {"name": name, "email": email, "phone": phone}
                set_view('loading')

elif st.session_state.view == 'loading':
    st.markdown("""
        <div style='text-align: center; padding: 100px 20px; background-color: #2563eb; color: white; border-radius: 25px;'>
            <h2 style='font-size: 2.5rem; font-weight: 900; font-style: italic; text-transform: uppercase;'>Cruzando Portais...</h2>
            <p style='opacity: 0.8;'>Aguarde enquanto nossa inteligência varre os portais imobiliários de Jaú.</p>
        </div>
    """, unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        progress_bar.progress(percent_complete + 1)
    
    # Agora chamamos a função que consulta o banco diretamente via st.connection
    search_results = search_properties_db(st.session_state.quiz_data)
    st.session_state.search_results = search_results
    
    if search_results:
        st.session_state.view = 'results'
    else:
        st.session_state.view = 'error'
    
    st.rerun()

elif st.session_state.view == 'error':
    st.error("Ocorreu um erro ao buscar os imóveis. Tente novamente mais tarde.")
    if st.button("Voltar ao Início", type="primary"):
        st.session_state.view = 'home'
        st.session_state.quiz_step = 0
        st.rerun()

elif st.session_state.view == 'results':
    if st.session_state.search_results:
        results = st.session_state.search_results
        properties = results.get('properties', [])
        total = results.get('total_results', 0)
        
        st.markdown(f"""
            <div style='background-color: #2563eb; padding: 40px; border-radius: 30px; color: white; margin-bottom: 40px;'>
                <h2 style='font-weight: 900; font-style: italic; text-transform: uppercase;'>Match Realizado!</h2>
                <p>Olá <b>{st.session_state.form_data['name']}</b>, encontramos <b>{total} imóvel(is)</b> de {st.session_state.quiz_data.get('property_type', 'imóveis')} em Jaú.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Nova Busca", key="new_search"):
            st.session_state.view = 'home'
            st.session_state.quiz_step = 0
            st.session_state.quiz_data = {}
            st.session_state.search_results = None
            st.rerun()

        if properties:
            cols = st.columns(2)
            for i, prop in enumerate(properties):
                with cols[i % 2]:
                    # Verificar se o preço é zerado
                    if prop['price'] == 0:
                        price_display = "Valor não informado"
                    else:
                        # Formatar preço no padrão brasileiro (vírgula como separador decimal)
                        price_formatted = f"{prop['price']:,.2f}".replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
                        price_display = f"R$ {price_formatted}"
                    
                    st.markdown(f"""
                        <div class="card">
                            <img src="{prop['image']}" style="width: 100%; border-radius: 15px; margin-bottom: 15px; height: 200px; object-fit: cover;">
                            <span class="badge">{prop['tag']}</span>
                            <h3 style="margin-top: 10px; font-weight: 900; font-size: 1.1rem;">{prop['type']} em {prop['neighborhood']}</h3>
                            <p class="property-price">{price_display}</p>
                            <p style="color: #6b7280; font-size: 0.8rem;">📍 {prop['neighborhood']}, Jaú/SP</p>
                            <p style="color: #9ca3af; font-size: 0.7rem; font-weight: bold;">CÓDIGO: {prop['code']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.link_button("VER DETALHES", prop['url'], use_container_width=True)
        else:
            st.warning("Nenhum imóvel encontrado com os critérios selecionados.")
            if st.button("Nova Busca"):
                st.session_state.view = 'home'
                st.session_state.quiz_step = 0
                st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 0.7rem; font-weight: bold; text-transform: uppercase;'>© 2026 JAÚ IMÓVEL NA MÃO • AGREGADOR INTELIGENTE</p>", unsafe_allow_html=True)
