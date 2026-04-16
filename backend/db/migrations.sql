-- Migração Inicial : eSocial Mensageria
-- Tabelas centrais para Gestão Multi-Tenant e Lotes de Eventos

-- 1. Empresas (Multi-tenant)
CREATE TABLE IF NOT EXISTS empresas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cnpj VARCHAR(14) UNIQUE NOT NULL,
    razao_social VARCHAR(200) NOT NULL,
    nome_fantasia VARCHAR(200),
    cert_base64 TEXT, -- Conteúdo do certificado PFX em Base64
    cert_password VARCHAR(200), -- Senha do certificado (preferencialmente vinda de Secrets)
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Lotes (Agrupamento de envios)
CREATE TABLE IF NOT EXISTS lotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID REFERENCES empresas(id) ON DELETE CASCADE,
    protocolo VARCHAR(50),
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, VALIDATING, SIGNED, SENT, PROCESSING, PROCESSED, ERROR
    ambiente VARCHAR(20) DEFAULT 'HOMOLOGATION',
    grupo_evento INTEGER,
    xml_original_url TEXT, -- Caminho no Supabase Storage
    xml_assinado_url TEXT, -- Caminho no Supabase Storage
    total_eventos INTEGER DEFAULT 0,
    eventos_sucesso INTEGER DEFAULT 0,
    eventos_erro INTEGER DEFAULT 0,
    erro_geral TEXT,
    tentativas_consulta INTEGER DEFAULT 0,
    proxima_consulta TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Eventos (Itens individuais do lote)
CREATE TABLE IF NOT EXISTS eventos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lote_id UUID REFERENCES lotes(id) ON DELETE CASCADE,
    evento_id_esocial VARCHAR(100),
    tipo VARCHAR(20),
    xml_original_url TEXT,
    xml_assinado_url TEXT,
    status VARCHAR(20) DEFAULT 'PENDING',
    nr_recibo VARCHAR(50),
    cd_resposta VARCHAR(10),
    desc_resposta TEXT,
    ocorrencias_json JSONB,
    validation_errors JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habilitar RLS (Row Level Security) mas por enquanto manter acesso via service_role livre
ALTER TABLE empresas ENABLE ROW LEVEL SECURITY;
ALTER TABLE lotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE eventos ENABLE ROW LEVEL SECURITY;
