--
-- PostgreSQL database dump
--

-- Dumped from database version 15.8
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: pg_database_owner
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO pg_database_owner;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: handle_updated_at(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.handle_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.handle_updated_at() OWNER TO postgres;

--
-- Name: sync_firebase_user(text, text, text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.sync_firebase_user(p_firebase_uid text, p_email text, p_display_name text DEFAULT NULL::text, p_photo_url text DEFAULT NULL::text) RETURNS uuid
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_user_id UUID;
BEGIN
    -- Try to insert or update user
    INSERT INTO users (firebase_uid, email, display_name, photo_url)
    VALUES (p_firebase_uid, p_email, p_display_name, p_photo_url)
    ON CONFLICT (firebase_uid) DO UPDATE
    SET 
        email = EXCLUDED.email,
        display_name = EXCLUDED.display_name,
        photo_url = EXCLUDED.photo_url,
        updated_at = NOW()
    RETURNING id INTO v_user_id;
    
    RETURN v_user_id;
END;
$$;


ALTER FUNCTION public.sync_firebase_user(p_firebase_uid text, p_email text, p_display_name text, p_photo_url text) OWNER TO postgres;

--
-- Name: update_sync_jobs_updated_at(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_sync_jobs_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_sync_jobs_updated_at() OWNER TO postgres;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: analytics_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analytics_events (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    profile_id text,
    event_type text NOT NULL,
    event_data jsonb DEFAULT '{}'::jsonb,
    "timestamp" timestamp with time zone NOT NULL,
    session_id uuid,
    data jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    sync_date date DEFAULT CURRENT_DATE,
    is_latest_for_date boolean DEFAULT true
);


ALTER TABLE public.analytics_events OWNER TO postgres;

--
-- Name: archetypes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.archetypes (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    profile_id text,
    name text,
    periodicity text,
    value text,
    data jsonb,
    start_date_time timestamp with time zone,
    end_date_time timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    user_id uuid,
    sahha_archetype_id text,
    data_type text,
    ordinality integer,
    version double precision DEFAULT 1.0,
    sync_date date,
    is_latest_for_date boolean DEFAULT true,
    start_date_only date
);


ALTER TABLE public.archetypes OWNER TO postgres;

--
-- Name: biomarkers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.biomarkers (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    profile_id text,
    category text,
    type text,
    data jsonb,
    start_date_time timestamp with time zone,
    end_date_time timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    user_id uuid,
    sahha_biomarker_id text,
    value text,
    unit text,
    value_type text,
    periodicity text,
    aggregation text,
    sync_date date,
    is_latest_for_date boolean DEFAULT true
);


ALTER TABLE public.biomarkers OWNER TO postgres;

--
-- Name: kpi_snapshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kpi_snapshots (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    profile_id text,
    snapshot_date date NOT NULL,
    window_type text NOT NULL,
    metrics_data jsonb NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    calculated_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    sync_date date DEFAULT CURRENT_DATE,
    is_latest_for_date boolean DEFAULT true,
    version double precision DEFAULT 1.0,
    CONSTRAINT kpi_snapshots_window_type_check CHECK ((window_type = ANY (ARRAY['daily'::text, 'weekly'::text, 'monthly'::text])))
);


ALTER TABLE public.kpi_snapshots OWNER TO postgres;

--
-- Name: memory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.memory (
    profile_id text NOT NULL,
    user_preferences jsonb DEFAULT '{}'::jsonb,
    health_goals jsonb DEFAULT '{}'::jsonb,
    dietary_restrictions jsonb DEFAULT '{}'::jsonb,
    lifestyle_context jsonb DEFAULT '{}'::jsonb,
    medical_conditions jsonb DEFAULT '{}'::jsonb,
    last_analysis_result text,
    analysis_insights jsonb DEFAULT '{}'::jsonb,
    last_nutrition_plan jsonb,
    last_routine_plan jsonb,
    last_behavior_analysis jsonb,
    transformation_seeker_plan jsonb,
    systematic_improver_plan jsonb,
    peak_performer_plan jsonb,
    resilience_rebuilder_plan jsonb,
    connected_explorer_plan jsonb,
    foundation_builder_plan jsonb,
    last_archetype text,
    health_trends jsonb DEFAULT '{}'::jsonb,
    improvement_areas jsonb DEFAULT '{}'::jsonb,
    success_patterns jsonb DEFAULT '{}'::jsonb,
    total_analyses integer DEFAULT 0,
    last_analysis_date timestamp with time zone,
    nutrition_plan_date timestamp with time zone,
    routine_plan_date timestamp with time zone,
    behavior_analysis_date timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    behavioral_signature jsonb DEFAULT '{}'::jsonb,
    sophistication_assessment jsonb DEFAULT '{}'::jsonb,
    primary_goal jsonb DEFAULT '{}'::jsonb,
    adaptive_parameters jsonb DEFAULT '{}'::jsonb,
    readiness_level character varying(50) DEFAULT NULL::character varying,
    habit_formation_stage character varying(100) DEFAULT NULL::character varying,
    recommendations jsonb DEFAULT '[]'::jsonb
);


ALTER TABLE public.memory OWNER TO postgres;

--
-- Name: notification_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_log (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    user_id uuid,
    template_id uuid,
    type character varying(50) NOT NULL,
    sent_at timestamp with time zone DEFAULT now(),
    opened_at timestamp with time zone,
    action_taken character varying(255),
    dismissed_at timestamp with time zone,
    context_data jsonb,
    simulation_run_id uuid
);


ALTER TABLE public.notification_log OWNER TO postgres;

--
-- Name: notification_queue; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_queue (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    user_id uuid,
    template_id uuid,
    scheduled_for timestamp with time zone NOT NULL,
    context_data jsonb,
    status character varying(50) DEFAULT 'pending'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    sent_at timestamp with time zone,
    error_message text,
    CONSTRAINT notification_queue_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'sent'::character varying, 'failed'::character varying, 'cancelled'::character varying])::text[])))
);


ALTER TABLE public.notification_queue OWNER TO postgres;

--
-- Name: notification_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_templates (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    name character varying(255) NOT NULL,
    title character varying(255) NOT NULL,
    body text NOT NULL,
    type character varying(50) DEFAULT 'in_app'::character varying,
    trigger_flags jsonb NOT NULL,
    priority integer DEFAULT 5,
    cooldown_hours integer DEFAULT 24,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT notification_templates_cooldown_hours_check CHECK ((cooldown_hours >= 0)),
    CONSTRAINT notification_templates_priority_check CHECK (((priority >= 1) AND (priority <= 10))),
    CONSTRAINT notification_templates_type_check CHECK (((type)::text = ANY ((ARRAY['in_app'::character varying, 'push'::character varying, 'email'::character varying])::text[])))
);


ALTER TABLE public.notification_templates OWNER TO postgres;

--
-- Name: profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.profiles (
    id text NOT NULL,
    data jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    user_id uuid,
    sahha_external_id text,
    sahha_profile_created_at timestamp without time zone,
    account_id text,
    last_webhook_received_at timestamp without time zone
);


ALTER TABLE public.profiles OWNER TO postgres;

--
-- Name: schedule_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedule_items (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    profile_id text,
    plan_id uuid,
    title text NOT NULL,
    description text,
    start_time timestamp with time zone NOT NULL,
    duration_minutes integer NOT NULL,
    category text,
    original_task_id text,
    is_custom boolean DEFAULT false,
    reminder_minutes integer DEFAULT 15,
    data jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    time_block text,
    task_source text DEFAULT 'user'::text,
    plan_archetype text,
    original_planned_time timestamp with time zone,
    CONSTRAINT chk_task_source CHECK ((task_source = ANY (ARRAY['user'::text, 'plan'::text, 'system'::text]))),
    CONSTRAINT chk_time_block CHECK (((time_block IS NULL) OR (time_block = ANY (ARRAY['morning_routine'::text, 'focus_blocks'::text, 'midday_reset'::text, 'evening_winddown'::text])))),
    CONSTRAINT schedule_items_duration_minutes_check CHECK ((duration_minutes > 0))
);


ALTER TABLE public.schedule_items OWNER TO postgres;

--
-- Name: COLUMN schedule_items.time_block; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.schedule_items.time_block IS 'Time block category: morning_routine, focus_blocks, midday_reset, evening_winddown';


--
-- Name: COLUMN schedule_items.task_source; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.schedule_items.task_source IS 'Source of the task: user (manually created), plan (from wellness plan), system (auto-generated)';


--
-- Name: COLUMN schedule_items.plan_archetype; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.schedule_items.plan_archetype IS 'Archetype name if task came from a wellness plan';


--
-- Name: scores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scores (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    profile_id text,
    type text,
    score double precision,
    data jsonb,
    score_date_time timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    user_id uuid,
    sahha_score_id text,
    state text,
    factors jsonb,
    data_sources text[],
    version double precision DEFAULT 1.0,
    sync_date date,
    is_latest_for_date boolean DEFAULT true
);


ALTER TABLE public.scores OWNER TO postgres;

--
-- Name: sync_jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sync_jobs (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    profile_id text,
    status text,
    data jsonb,
    created_at timestamp with time zone DEFAULT now(),
    completed_at timestamp with time zone,
    success boolean,
    user_id character varying(255),
    job_type character varying(100),
    progress numeric(5,2) DEFAULT 0.0,
    current_step integer DEFAULT 0,
    total_steps integer DEFAULT 0,
    current_message text,
    started_at timestamp with time zone,
    updated_at timestamp with time zone DEFAULT now(),
    metadata jsonb,
    error text,
    results jsonb,
    sync_date date,
    data_type character varying(50),
    metric_type character varying(50)
);


ALTER TABLE public.sync_jobs OWNER TO postgres;

--
-- Name: task_completions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_completions (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    profile_id text,
    plan_id uuid,
    task_id uuid NOT NULL,
    completed_at timestamp with time zone NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now(),
    sync_date date DEFAULT CURRENT_DATE,
    is_latest_for_date boolean DEFAULT true,
    planned_time timestamp with time zone
);


ALTER TABLE public.task_completions OWNER TO postgres;

--
-- Name: user_context_flags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_context_flags (
    user_id uuid NOT NULL,
    flags jsonb NOT NULL,
    generated_at timestamp with time zone DEFAULT now(),
    kpi_snapshot_id uuid
);


ALTER TABLE public.user_context_flags OWNER TO postgres;

--
-- Name: user_notification_preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_notification_preferences (
    user_id uuid NOT NULL,
    in_app_enabled boolean DEFAULT true,
    push_enabled boolean DEFAULT false,
    email_enabled boolean DEFAULT false,
    quiet_hours_start time without time zone DEFAULT '22:00:00'::time without time zone,
    quiet_hours_end time without time zone DEFAULT '07:00:00'::time without time zone,
    max_daily_notifications integer DEFAULT 5,
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT user_notification_preferences_max_daily_notifications_check CHECK ((max_daily_notifications >= 0))
);


ALTER TABLE public.user_notification_preferences OWNER TO postgres;

--
-- Name: user_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_sessions (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    profile_id text,
    session_token text NOT NULL,
    device_info jsonb DEFAULT '{}'::jsonb,
    ip_address inet,
    user_agent text,
    firebase_token text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone NOT NULL,
    last_activity timestamp with time zone DEFAULT now()
);


ALTER TABLE public.user_sessions OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    firebase_uid text NOT NULL,
    email text,
    display_name text,
    photo_url text,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: waitlist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.waitlist (
    id uuid NOT NULL,
    name text,
    email text,
    created_at timestamp with time zone,
    status text,
    notes text,
    source text
);


ALTER TABLE public.waitlist OWNER TO postgres;

--
-- Name: webhook_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.webhook_events (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    event_type text NOT NULL,
    external_id text NOT NULL,
    signature text NOT NULL,
    payload jsonb NOT NULL,
    processed boolean DEFAULT false,
    processed_at timestamp without time zone,
    error text,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.webhook_events OWNER TO postgres;

--
-- Name: wellness_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.wellness_plans (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    profile_id text,
    name text NOT NULL,
    archetype text NOT NULL,
    plan_data jsonb NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT wellness_plans_archetype_check CHECK ((archetype = ANY (ARRAY['peak'::text, 'systematic'::text, 'transform'::text, 'foundation'::text, 'resilience'::text, 'connected'::text])))
);


ALTER TABLE public.wellness_plans OWNER TO postgres;

--
-- Name: memory ai_memory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.memory
    ADD CONSTRAINT ai_memory_pkey PRIMARY KEY (profile_id);


--
-- Name: analytics_events analytics_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analytics_events
    ADD CONSTRAINT analytics_events_pkey PRIMARY KEY (id);


--
-- Name: archetypes archetypes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archetypes
    ADD CONSTRAINT archetypes_pkey PRIMARY KEY (id);


--
-- Name: biomarkers biomarkers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.biomarkers
    ADD CONSTRAINT biomarkers_pkey PRIMARY KEY (id);


--
-- Name: kpi_snapshots kpi_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kpi_snapshots
    ADD CONSTRAINT kpi_snapshots_pkey PRIMARY KEY (id);


--
-- Name: notification_log notification_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_log
    ADD CONSTRAINT notification_log_pkey PRIMARY KEY (id);


--
-- Name: notification_queue notification_queue_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_queue
    ADD CONSTRAINT notification_queue_pkey PRIMARY KEY (id);


--
-- Name: notification_templates notification_templates_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_templates
    ADD CONSTRAINT notification_templates_name_key UNIQUE (name);


--
-- Name: notification_templates notification_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_templates
    ADD CONSTRAINT notification_templates_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_sahha_external_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_sahha_external_id_key UNIQUE (sahha_external_id);


--
-- Name: schedule_items schedule_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_items
    ADD CONSTRAINT schedule_items_pkey PRIMARY KEY (id);


--
-- Name: scores scores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scores
    ADD CONSTRAINT scores_pkey PRIMARY KEY (id);


--
-- Name: sync_jobs sync_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sync_jobs
    ADD CONSTRAINT sync_jobs_pkey PRIMARY KEY (id);


--
-- Name: task_completions task_completions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_completions
    ADD CONSTRAINT task_completions_pkey PRIMARY KEY (id);


--
-- Name: wellness_plans unique_active_plan; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wellness_plans
    ADD CONSTRAINT unique_active_plan EXCLUDE USING btree (user_id WITH =) WHERE ((is_active = true));


--
-- Name: kpi_snapshots unique_snapshot_per_date; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kpi_snapshots
    ADD CONSTRAINT unique_snapshot_per_date UNIQUE (user_id, snapshot_date, window_type);


--
-- Name: sync_jobs unique_sync_job_per_date_type; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sync_jobs
    ADD CONSTRAINT unique_sync_job_per_date_type UNIQUE (profile_id, sync_date, data_type);


--
-- Name: user_context_flags user_context_flags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_context_flags
    ADD CONSTRAINT user_context_flags_pkey PRIMARY KEY (user_id);


--
-- Name: user_notification_preferences user_notification_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_notification_preferences
    ADD CONSTRAINT user_notification_preferences_pkey PRIMARY KEY (user_id);


--
-- Name: user_sessions user_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_pkey PRIMARY KEY (id);


--
-- Name: user_sessions user_sessions_session_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT user_sessions_session_token_key UNIQUE (session_token);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_firebase_uid_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_firebase_uid_key UNIQUE (firebase_uid);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: waitlist waitlist_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.waitlist
    ADD CONSTRAINT waitlist_pkey PRIMARY KEY (id);


--
-- Name: webhook_events webhook_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webhook_events
    ADD CONSTRAINT webhook_events_pkey PRIMARY KEY (id);


--
-- Name: wellness_plans wellness_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wellness_plans
    ADD CONSTRAINT wellness_plans_pkey PRIMARY KEY (id);


--
-- Name: archetypes_name_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX archetypes_name_idx ON public.archetypes USING btree (name);


--
-- Name: archetypes_periodicity_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX archetypes_periodicity_idx ON public.archetypes USING btree (periodicity);


--
-- Name: archetypes_profile_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX archetypes_profile_id_idx ON public.archetypes USING btree (profile_id);


--
-- Name: biomarkers_category_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX biomarkers_category_idx ON public.biomarkers USING btree (category);


--
-- Name: biomarkers_profile_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX biomarkers_profile_id_idx ON public.biomarkers USING btree (profile_id);


--
-- Name: biomarkers_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX biomarkers_type_idx ON public.biomarkers USING btree (type);


--
-- Name: idx_ai_memory_last_analysis_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ai_memory_last_analysis_date ON public.memory USING btree (last_analysis_date);


--
-- Name: idx_ai_memory_profile_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ai_memory_profile_id ON public.memory USING btree (profile_id);


--
-- Name: idx_archetypes_is_latest_for_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_archetypes_is_latest_for_date ON public.archetypes USING btree (is_latest_for_date);


--
-- Name: idx_archetypes_latest_composite; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_archetypes_latest_composite ON public.archetypes USING btree (profile_id, start_date_only, is_latest_for_date) WHERE (is_latest_for_date = true);


--
-- Name: idx_archetypes_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_archetypes_name ON public.archetypes USING btree (name);


--
-- Name: idx_archetypes_periodicity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_archetypes_periodicity ON public.archetypes USING btree (periodicity);


--
-- Name: idx_archetypes_profile_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_archetypes_profile_id ON public.archetypes USING btree (profile_id);


--
-- Name: idx_archetypes_profile_sync_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_archetypes_profile_sync_date ON public.archetypes USING btree (profile_id, sync_date);


--
-- Name: idx_archetypes_sync_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_archetypes_sync_date ON public.archetypes USING btree (sync_date);


--
-- Name: idx_archetypes_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_archetypes_user_id ON public.archetypes USING btree (user_id);


--
-- Name: idx_biomarkers_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_biomarkers_category ON public.biomarkers USING btree (category);


--
-- Name: idx_biomarkers_dates; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_biomarkers_dates ON public.biomarkers USING btree (start_date_time, end_date_time);


--
-- Name: idx_biomarkers_profile_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_biomarkers_profile_id ON public.biomarkers USING btree (profile_id);


--
-- Name: idx_biomarkers_sync_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_biomarkers_sync_date ON public.biomarkers USING btree (profile_id, sync_date, is_latest_for_date);


--
-- Name: idx_biomarkers_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_biomarkers_type ON public.biomarkers USING btree (type);


--
-- Name: idx_biomarkers_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_biomarkers_user_id ON public.biomarkers USING btree (user_id);


--
-- Name: idx_notification_log_template_sent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_log_template_sent ON public.notification_log USING btree (template_id, sent_at DESC);


--
-- Name: idx_notification_log_user_sent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_log_user_sent ON public.notification_log USING btree (user_id, sent_at DESC);


--
-- Name: idx_notification_queue_scheduled; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_queue_scheduled ON public.notification_queue USING btree (scheduled_for) WHERE ((status)::text = 'pending'::text);


--
-- Name: idx_notification_templates_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_templates_active ON public.notification_templates USING btree (is_active) WHERE (is_active = true);


--
-- Name: idx_profiles_external_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_profiles_external_id ON public.profiles USING btree (sahha_external_id);


--
-- Name: idx_profiles_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_profiles_user_id ON public.profiles USING btree (user_id);


--
-- Name: idx_schedule_items_categories; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_items_categories ON public.schedule_items USING btree (user_id, category, time_block, start_time);


--
-- Name: idx_schedule_items_task_source; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_items_task_source ON public.schedule_items USING btree (task_source, user_id);


--
-- Name: idx_schedule_items_time_block; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_items_time_block ON public.schedule_items USING btree (time_block, start_time);


--
-- Name: idx_scores_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_scores_date ON public.scores USING btree (score_date_time DESC);


--
-- Name: idx_scores_profile_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_scores_profile_id ON public.scores USING btree (profile_id);


--
-- Name: idx_scores_sync_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_scores_sync_date ON public.scores USING btree (profile_id, sync_date, is_latest_for_date);


--
-- Name: idx_scores_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_scores_type ON public.scores USING btree (type);


--
-- Name: idx_scores_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_scores_user_id ON public.scores USING btree (user_id);


--
-- Name: idx_sync_jobs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sync_jobs_created_at ON public.sync_jobs USING btree (created_at);


--
-- Name: idx_sync_jobs_date_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sync_jobs_date_type ON public.sync_jobs USING btree (profile_id, sync_date, data_type);


--
-- Name: idx_sync_jobs_profile_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sync_jobs_profile_id ON public.sync_jobs USING btree (profile_id);


--
-- Name: idx_sync_jobs_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sync_jobs_status ON public.sync_jobs USING btree (status);


--
-- Name: idx_sync_jobs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sync_jobs_user_id ON public.sync_jobs USING btree (user_id);


--
-- Name: idx_user_context_flags_generated; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_context_flags_generated ON public.user_context_flags USING btree (generated_at DESC);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: idx_users_firebase_uid; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_firebase_uid ON public.users USING btree (firebase_uid);


--
-- Name: idx_webhook_events_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_webhook_events_created_at ON public.webhook_events USING btree (created_at DESC);


--
-- Name: idx_webhook_events_event_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_webhook_events_event_type ON public.webhook_events USING btree (event_type);


--
-- Name: idx_webhook_events_external_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_webhook_events_external_id ON public.webhook_events USING btree (external_id);


--
-- Name: idx_webhook_events_processed; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_webhook_events_processed ON public.webhook_events USING btree (processed);


--
-- Name: scores_profile_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX scores_profile_id_idx ON public.scores USING btree (profile_id);


--
-- Name: scores_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX scores_type_idx ON public.scores USING btree (type);


--
-- Name: sync_jobs_profile_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX sync_jobs_profile_id_idx ON public.sync_jobs USING btree (profile_id);


--
-- Name: memory handle_ai_memory_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER handle_ai_memory_updated_at BEFORE UPDATE ON public.memory FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();


--
-- Name: kpi_snapshots update_kpi_snapshots_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_kpi_snapshots_updated_at BEFORE UPDATE ON public.kpi_snapshots FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: notification_templates update_notification_templates_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_notification_templates_updated_at BEFORE UPDATE ON public.notification_templates FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: schedule_items update_schedule_items_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_schedule_items_updated_at BEFORE UPDATE ON public.schedule_items FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: sync_jobs update_sync_jobs_updated_at_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_sync_jobs_updated_at_trigger BEFORE UPDATE ON public.sync_jobs FOR EACH ROW EXECUTE FUNCTION public.update_sync_jobs_updated_at();


--
-- Name: user_notification_preferences update_user_notification_preferences_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_user_notification_preferences_updated_at BEFORE UPDATE ON public.user_notification_preferences FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: user_sessions update_user_sessions_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_user_sessions_updated_at BEFORE UPDATE ON public.user_sessions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: wellness_plans update_wellness_plans_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_wellness_plans_updated_at BEFORE UPDATE ON public.wellness_plans FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: archetypes archetypes_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archetypes
    ADD CONSTRAINT archetypes_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id);


--
-- Name: biomarkers biomarkers_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.biomarkers
    ADD CONSTRAINT biomarkers_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id);


--
-- Name: analytics_events fk_analytics_events_profile; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analytics_events
    ADD CONSTRAINT fk_analytics_events_profile FOREIGN KEY (profile_id) REFERENCES public.profiles(id) ON DELETE SET NULL;


--
-- Name: analytics_events fk_analytics_events_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analytics_events
    ADD CONSTRAINT fk_analytics_events_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: archetypes fk_archetypes_profile; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archetypes
    ADD CONSTRAINT fk_archetypes_profile FOREIGN KEY (profile_id) REFERENCES public.profiles(id) ON DELETE CASCADE;


--
-- Name: archetypes fk_archetypes_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.archetypes
    ADD CONSTRAINT fk_archetypes_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: biomarkers fk_biomarkers_profile; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.biomarkers
    ADD CONSTRAINT fk_biomarkers_profile FOREIGN KEY (profile_id) REFERENCES public.profiles(id) ON DELETE CASCADE;


--
-- Name: biomarkers fk_biomarkers_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.biomarkers
    ADD CONSTRAINT fk_biomarkers_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: kpi_snapshots fk_kpi_snapshots_profile; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kpi_snapshots
    ADD CONSTRAINT fk_kpi_snapshots_profile FOREIGN KEY (profile_id) REFERENCES public.profiles(id) ON DELETE SET NULL;


--
-- Name: kpi_snapshots fk_kpi_snapshots_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kpi_snapshots
    ADD CONSTRAINT fk_kpi_snapshots_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: profiles fk_profiles_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT fk_profiles_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: schedule_items fk_schedule_items_plan; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_items
    ADD CONSTRAINT fk_schedule_items_plan FOREIGN KEY (plan_id) REFERENCES public.wellness_plans(id) ON DELETE SET NULL;


--
-- Name: schedule_items fk_schedule_items_profile; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_items
    ADD CONSTRAINT fk_schedule_items_profile FOREIGN KEY (profile_id) REFERENCES public.profiles(id) ON DELETE SET NULL;


--
-- Name: schedule_items fk_schedule_items_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_items
    ADD CONSTRAINT fk_schedule_items_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: scores fk_scores_profile; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scores
    ADD CONSTRAINT fk_scores_profile FOREIGN KEY (profile_id) REFERENCES public.profiles(id) ON DELETE CASCADE;


--
-- Name: scores fk_scores_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scores
    ADD CONSTRAINT fk_scores_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: task_completions fk_task_completions_plan; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_completions
    ADD CONSTRAINT fk_task_completions_plan FOREIGN KEY (plan_id) REFERENCES public.wellness_plans(id) ON DELETE SET NULL;


--
-- Name: task_completions fk_task_completions_profile; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_completions
    ADD CONSTRAINT fk_task_completions_profile FOREIGN KEY (profile_id) REFERENCES public.profiles(id) ON DELETE SET NULL;


--
-- Name: task_completions fk_task_completions_schedule_items; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_completions
    ADD CONSTRAINT fk_task_completions_schedule_items FOREIGN KEY (task_id) REFERENCES public.schedule_items(id) ON DELETE CASCADE;


--
-- Name: task_completions fk_task_completions_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_completions
    ADD CONSTRAINT fk_task_completions_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_sessions fk_user_sessions_profile; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT fk_user_sessions_profile FOREIGN KEY (profile_id) REFERENCES public.profiles(id) ON DELETE SET NULL;


--
-- Name: user_sessions fk_user_sessions_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_sessions
    ADD CONSTRAINT fk_user_sessions_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: wellness_plans fk_wellness_plans_profile; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wellness_plans
    ADD CONSTRAINT fk_wellness_plans_profile FOREIGN KEY (profile_id) REFERENCES public.profiles(id) ON DELETE SET NULL;


--
-- Name: wellness_plans fk_wellness_plans_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wellness_plans
    ADD CONSTRAINT fk_wellness_plans_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: notification_log notification_log_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_log
    ADD CONSTRAINT notification_log_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.notification_templates(id) ON DELETE SET NULL;


--
-- Name: notification_log notification_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_log
    ADD CONSTRAINT notification_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: notification_queue notification_queue_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_queue
    ADD CONSTRAINT notification_queue_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.notification_templates(id) ON DELETE CASCADE;


--
-- Name: notification_queue notification_queue_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_queue
    ADD CONSTRAINT notification_queue_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: scores scores_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scores
    ADD CONSTRAINT scores_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id);


--
-- Name: sync_jobs sync_jobs_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sync_jobs
    ADD CONSTRAINT sync_jobs_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id);


--
-- Name: user_context_flags user_context_flags_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_context_flags
    ADD CONSTRAINT user_context_flags_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_notification_preferences user_notification_preferences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_notification_preferences
    ADD CONSTRAINT user_notification_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: notification_templates Templates are readable by authenticated users; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY "Templates are readable by authenticated users" ON public.notification_templates FOR SELECT TO authenticated USING (true);


--
-- Name: user_context_flags Users can view own context flags; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY "Users can view own context flags" ON public.user_context_flags TO authenticated USING ((auth.uid() = user_id));


--
-- Name: notification_log Users can view own notification log; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY "Users can view own notification log" ON public.notification_log TO authenticated USING ((auth.uid() = user_id));


--
-- Name: notification_queue Users can view own notification queue; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY "Users can view own notification queue" ON public.notification_queue TO authenticated USING ((auth.uid() = user_id));


--
-- Name: user_notification_preferences Users can view own preferences; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY "Users can view own preferences" ON public.user_notification_preferences TO authenticated USING ((auth.uid() = user_id));


--
-- Name: analytics_events analytics_events_user_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY analytics_events_user_policy ON public.analytics_events USING ((user_id = auth.uid()));


--
-- Name: kpi_snapshots kpi_snapshots_user_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY kpi_snapshots_user_policy ON public.kpi_snapshots USING ((user_id = auth.uid()));


--
-- Name: schedule_items schedule_items_user_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY schedule_items_user_policy ON public.schedule_items USING ((user_id = auth.uid()));


--
-- Name: task_completions task_completions_user_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY task_completions_user_policy ON public.task_completions USING ((user_id = auth.uid()));


--
-- Name: user_sessions user_sessions_user_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY user_sessions_user_policy ON public.user_sessions USING ((user_id = auth.uid()));


--
-- Name: wellness_plans wellness_plans_delete_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY wellness_plans_delete_policy ON public.wellness_plans FOR DELETE USING ((user_id = ( SELECT auth.uid() AS uid)));


--
-- Name: wellness_plans wellness_plans_insert_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY wellness_plans_insert_policy ON public.wellness_plans FOR INSERT WITH CHECK ((user_id = ( SELECT auth.uid() AS uid)));


--
-- Name: wellness_plans wellness_plans_select_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY wellness_plans_select_policy ON public.wellness_plans FOR SELECT USING ((user_id = ( SELECT auth.uid() AS uid)));


--
-- Name: wellness_plans wellness_plans_update_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY wellness_plans_update_policy ON public.wellness_plans FOR UPDATE USING ((user_id = ( SELECT auth.uid() AS uid))) WITH CHECK ((user_id = ( SELECT auth.uid() AS uid)));


--
-- Name: wellness_plans wellness_plans_user_policy; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY wellness_plans_user_policy ON public.wellness_plans USING ((user_id = auth.uid()));


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO postgres;
GRANT USAGE ON SCHEMA public TO anon;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO service_role;


--
-- Name: FUNCTION handle_updated_at(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.handle_updated_at() TO anon;
GRANT ALL ON FUNCTION public.handle_updated_at() TO authenticated;
GRANT ALL ON FUNCTION public.handle_updated_at() TO service_role;


--
-- Name: FUNCTION sync_firebase_user(p_firebase_uid text, p_email text, p_display_name text, p_photo_url text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.sync_firebase_user(p_firebase_uid text, p_email text, p_display_name text, p_photo_url text) TO anon;
GRANT ALL ON FUNCTION public.sync_firebase_user(p_firebase_uid text, p_email text, p_display_name text, p_photo_url text) TO authenticated;
GRANT ALL ON FUNCTION public.sync_firebase_user(p_firebase_uid text, p_email text, p_display_name text, p_photo_url text) TO service_role;


--
-- Name: FUNCTION update_sync_jobs_updated_at(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.update_sync_jobs_updated_at() TO anon;
GRANT ALL ON FUNCTION public.update_sync_jobs_updated_at() TO authenticated;
GRANT ALL ON FUNCTION public.update_sync_jobs_updated_at() TO service_role;


--
-- Name: FUNCTION update_updated_at_column(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.update_updated_at_column() TO anon;
GRANT ALL ON FUNCTION public.update_updated_at_column() TO authenticated;
GRANT ALL ON FUNCTION public.update_updated_at_column() TO service_role;


--
-- Name: TABLE analytics_events; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.analytics_events TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.analytics_events TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.analytics_events TO service_role;


--
-- Name: TABLE archetypes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.archetypes TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.archetypes TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.archetypes TO service_role;


--
-- Name: TABLE biomarkers; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.biomarkers TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.biomarkers TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.biomarkers TO service_role;


--
-- Name: TABLE kpi_snapshots; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.kpi_snapshots TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.kpi_snapshots TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.kpi_snapshots TO service_role;


--
-- Name: TABLE memory; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.memory TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.memory TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.memory TO service_role;


--
-- Name: TABLE notification_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.notification_log TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.notification_log TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.notification_log TO service_role;


--
-- Name: TABLE notification_queue; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.notification_queue TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.notification_queue TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.notification_queue TO service_role;


--
-- Name: TABLE notification_templates; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.notification_templates TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.notification_templates TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.notification_templates TO service_role;


--
-- Name: TABLE profiles; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.profiles TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.profiles TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.profiles TO service_role;


--
-- Name: TABLE schedule_items; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.schedule_items TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.schedule_items TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.schedule_items TO service_role;


--
-- Name: TABLE scores; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.scores TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.scores TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.scores TO service_role;


--
-- Name: TABLE sync_jobs; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.sync_jobs TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.sync_jobs TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.sync_jobs TO service_role;


--
-- Name: TABLE task_completions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.task_completions TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.task_completions TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.task_completions TO service_role;


--
-- Name: TABLE user_context_flags; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.user_context_flags TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.user_context_flags TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.user_context_flags TO service_role;


--
-- Name: TABLE user_notification_preferences; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.user_notification_preferences TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.user_notification_preferences TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.user_notification_preferences TO service_role;


--
-- Name: TABLE user_sessions; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.user_sessions TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.user_sessions TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.user_sessions TO service_role;


--
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.users TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.users TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.users TO service_role;


--
-- Name: TABLE waitlist; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.waitlist TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.waitlist TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.waitlist TO service_role;


--
-- Name: TABLE webhook_events; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.webhook_events TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.webhook_events TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.webhook_events TO service_role;


--
-- Name: TABLE wellness_plans; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.wellness_plans TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.wellness_plans TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.wellness_plans TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: public; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON FUNCTIONS TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON FUNCTIONS TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON FUNCTIONS TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON FUNCTIONS TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: supabase_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO service_role;


--
-- PostgreSQL database dump complete
--

