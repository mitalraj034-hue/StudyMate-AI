def get_studymate_swagger_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StudyMate AI — Interactive API Documentation</title>
    
    <!-- Modern Typography: Inter & JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Swagger UI Default CSS -->
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%234f46e5' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z'></path><path d='M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z'></path></svg>">

    <style>
        /* ==========================================================================
           StudyMate AI — Custom Premium Swagger UI Theme
           ========================================================================== */

        :root {
            --sm-primary: #4f46e5;
            --sm-primary-dark: #3730a3;
            --sm-primary-light: #eef2ff;
            --sm-purple: #7c3aed;
            --sm-purple-light: #f5f3ff;
            --sm-cyan: #06b6d4;
            --sm-slate-950: #020617;
            --sm-slate-900: #0f172a;
            --sm-slate-850: #141e33;
            --sm-slate-800: #1e293b;
            --sm-slate-700: #334155;
            --sm-slate-600: #475569;
            --sm-slate-500: #64748b;
            --sm-slate-400: #94a3b8;
            --sm-slate-300: #cbd5e1;
            --sm-slate-200: #e2e8f0;
            --sm-slate-100: #f1f5f9;
            --sm-slate-50: #f8fafc;
            --sm-white: #ffffff;
            --sm-card-radius: 12px;
            --sm-btn-radius: 8px;
            --sm-font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --sm-font-mono: 'JetBrains Mono', monospace;
            
            /* Theme Dynamic Variables (Light Theme Default) */
            --bg-page: var(--sm-slate-50);
            --bg-card: var(--sm-white);
            --bg-card-subtle: #fafafa;
            --border-color: var(--sm-slate-200);
            --border-hover: #cbd5e1;
            --text-main: var(--sm-slate-900);
            --text-muted: var(--sm-slate-600);
            --text-dim: var(--sm-slate-400);
            --shadow-card: 0 2px 8px -2px rgba(0, 0, 0, 0.05);
            --shadow-hover: 0 8px 20px -4px rgba(0, 0, 0, 0.08);
            --input-bg: var(--sm-white);
            --input-border: var(--sm-slate-300);
        }

        /* Dark Mode Overrides */
        body.dark {
            --bg-page: #0b0f19;
            --bg-card: #111827;
            --bg-card-subtle: #162032;
            --border-color: #1f293d;
            --border-hover: #374151;
            --text-main: #f8fafc;
            --text-muted: #cbd5e1;
            --text-dim: #94a3b8;
            --shadow-card: 0 4px 12px rgba(0, 0, 0, 0.3);
            --shadow-hover: 0 10px 25px rgba(0, 0, 0, 0.4);
            --input-bg: #0f172a;
            --input-border: #334155;
        }

        /* Global Reset & Typography */
        *, *::before, *::after {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 0;
            background-color: var(--bg-page);
            font-family: var(--sm-font-sans) !important;
            color: var(--text-main);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            transition: background-color 0.2s ease, color 0.2s ease;
        }

        .swagger-ui {
            font-family: var(--sm-font-sans) !important;
            color: var(--text-main);
        }

        /* Hide the default swagger topbar */
        .swagger-ui .topbar {
            display: none !important;
        }

        /* Custom StudyMate AI Branding Top Header */
        .studymate-brand-header {
            background: linear-gradient(135deg, #0b0f19 0%, #171c35 50%, #0f172a 100%);
            color: var(--sm-white);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 22px 32px;
            box-shadow: 0 4px 25px -2px rgba(0, 0, 0, 0.2);
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(12px);
        }

        .studymate-brand-container {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
        }

        .studymate-brand-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .studymate-brand-logo {
            width: 46px;
            height: 46px;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            box-shadow: 0 8px 20px -4px rgba(79, 70, 229, 0.5);
            font-size: 24px;
            flex-shrink: 0;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }

        .studymate-brand-titles h1 {
            margin: 0;
            font-size: 22px;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: var(--sm-white);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .studymate-brand-titles .badge-pill {
            font-size: 11px;
            font-weight: 700;
            background: rgba(99, 102, 241, 0.25);
            color: #a5b4fc;
            padding: 2px 8px;
            border-radius: 6px;
            border: 1px solid rgba(165, 180, 252, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .studymate-brand-titles p.subtitle {
            margin: 3px 0 0 0;
            font-size: 13px;
            font-weight: 600;
            color: #c7d2fe;
        }

        .studymate-brand-titles p.description {
            margin: 4px 0 0 0;
            font-size: 12px;
            color: #94a3b8;
            max-width: 680px;
            line-height: 1.45;
        }

        .studymate-brand-actions {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
        }

        .badge-status {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 10px #10b981;
            animation: pulse-dot 2s infinite;
        }

        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.9); }
        }

        .btn-header-link {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #e2e8f0;
            padding: 7px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-header-link:hover {
            background: rgba(255, 255, 255, 0.18);
            color: var(--sm-white);
            transform: translateY(-1px);
        }

        .btn-theme-toggle {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #f1f5f9;
            padding: 7px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }

        .btn-theme-toggle:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }

        /* Swagger Container Wrapper */
        .swagger-ui .wrapper {
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px 32px;
        }

        /* Info container */
        .swagger-ui .info {
            margin: 16px 0 24px 0;
            padding: 24px 28px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--sm-card-radius);
            box-shadow: var(--shadow-card);
        }

        .swagger-ui .info .title {
            font-size: 26px;
            font-weight: 800;
            color: var(--text-main);
            letter-spacing: -0.5px;
            font-family: var(--sm-font-sans);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .swagger-ui .info .title small.version-stamp {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            border-radius: 6px;
            font-size: 12px;
            padding: 3px 10px;
            font-weight: 700;
        }

        .swagger-ui .info p {
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.6;
            margin-top: 8px;
        }

        /* Modern Filter / Search Bar */
        .swagger-ui .filter-container {
            padding: 14px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--sm-card-radius);
            box-shadow: var(--shadow-card);
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .swagger-ui .filter-container::before {
            content: "🔍";
            font-size: 14px;
            opacity: 0.7;
        }

        .swagger-ui .filter-container input {
            border: 1px solid var(--input-border) !important;
            border-radius: 20px !important;
            padding: 9px 18px !important;
            font-size: 13px !important;
            font-family: var(--sm-font-sans) !important;
            background-color: var(--input-bg) !important;
            color: var(--text-main) !important;
            transition: all 0.2s ease;
            width: 100% !important;
            max-width: 500px !important;
        }

        .swagger-ui .filter-container input:focus {
            outline: none !important;
            border-color: var(--sm-primary) !important;
            background-color: var(--bg-card) !important;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2) !important;
        }

        /* Special Styling for Authorize Button */
        .swagger-ui .auth-wrapper {
            margin-bottom: 20px;
            display: flex;
            justify-content: flex-end;
        }

        .swagger-ui .btn.authorize {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: var(--sm-btn-radius) !important;
            padding: 10px 24px !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            font-family: var(--sm-font-sans) !important;
            box-shadow: 0 4px 15px -2px rgba(79, 70, 229, 0.45) !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 8px !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }

        .swagger-ui .btn.authorize:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 22px -2px rgba(79, 70, 229, 0.6) !important;
        }

        .swagger-ui .btn.authorize svg {
            fill: #ffffff !important;
            width: 16px;
            height: 16px;
        }

        /* API Group Sections (Tags) */
        .swagger-ui .opblock-tag-section {
            margin-bottom: 28px;
        }

        .swagger-ui .opblock-tag {
            font-family: var(--sm-font-sans) !important;
            font-size: 17px !important;
            font-weight: 700 !important;
            color: var(--text-main) !important;
            padding: 16px 22px !important;
            border-bottom: 2px solid var(--border-color) !important;
            background: var(--bg-card);
            border-radius: var(--sm-card-radius) var(--sm-card-radius) 0 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s;
            box-shadow: var(--shadow-card);
        }

        .swagger-ui .opblock-tag small {
            font-size: 12px !important;
            color: var(--text-muted) !important;
            font-weight: 500 !important;
        }

        .swagger-ui .opblock-tag:hover {
            background-color: var(--bg-card-subtle);
        }

        /* Modern Endpoint Cards */
        .swagger-ui .opblock {
            margin: 10px 0 !important;
            border-radius: var(--sm-card-radius) !important;
            box-shadow: var(--shadow-card) !important;
            border: 1px solid var(--border-color) !important;
            background: var(--bg-card) !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
            overflow: hidden;
        }

        .swagger-ui .opblock:hover {
            box-shadow: var(--shadow-hover) !important;
            transform: translateY(-1.5px);
            border-color: var(--border-hover) !important;
        }

        .swagger-ui .opblock .opblock-summary {
            padding: 13px 20px !important;
            display: flex;
            align-items: center;
            border-bottom: none !important;
        }

        /* Distinct Modern Method Badges */
        .swagger-ui .opblock .opblock-summary-method {
            font-family: var(--sm-font-mono) !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
            padding: 6px 14px !important;
            min-width: 72px !important;
            text-align: center;
            text-shadow: none !important;
            letter-spacing: 0.5px;
        }

        /* POST: Indigo Gradient */
        .swagger-ui .opblock.opblock-post {
            border-color: rgba(79, 70, 229, 0.3) !important;
            background: var(--bg-card) !important;
        }
        .swagger-ui .opblock.opblock-post .opblock-summary-method {
            background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
        }

        /* GET: Emerald Gradient */
        .swagger-ui .opblock.opblock-get {
            border-color: rgba(16, 185, 129, 0.3) !important;
            background: var(--bg-card) !important;
        }
        .swagger-ui .opblock.opblock-get .opblock-summary-method {
            background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
        }

        /* PUT: Amber Gradient */
        .swagger-ui .opblock.opblock-put {
            border-color: rgba(245, 158, 11, 0.3) !important;
            background: var(--bg-card) !important;
        }
        .swagger-ui .opblock.opblock-put .opblock-summary-method {
            background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
        }

        /* DELETE: Rose Gradient */
        .swagger-ui .opblock.opblock-delete {
            border-color: rgba(244, 63, 94, 0.3) !important;
            background: var(--bg-card) !important;
        }
        .swagger-ui .opblock.opblock-delete .opblock-summary-method {
            background: linear-gradient(135deg, #e11d48 0%, #f43f5e 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 2px 8px rgba(244, 63, 94, 0.3);
        }

        /* Endpoint Path Typography */
        .swagger-ui .opblock .opblock-summary-path {
            font-family: var(--sm-font-mono) !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            color: var(--text-main) !important;
            padding-left: 14px;
        }

        .swagger-ui .opblock .opblock-summary-description {
            font-family: var(--sm-font-sans) !important;
            font-size: 13px !important;
            color: var(--text-muted) !important;
            font-weight: 500 !important;
            margin-left: auto;
            padding-right: 12px;
        }

        /* Operation Details Container (Expanded Card) */
        .swagger-ui .opblock-body {
            background: var(--bg-card-subtle) !important;
            border-top: 1px solid var(--border-color);
            padding: 22px !important;
        }

        /* Modern Interactive Buttons: Try it out, Execute, Cancel, Clear */
        .swagger-ui .btn {
            border-radius: var(--sm-btn-radius) !important;
            font-family: var(--sm-font-sans) !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            padding: 8px 18px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }

        .swagger-ui .btn.try-out__btn {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-muted) !important;
        }

        .swagger-ui .btn.try-out__btn:hover {
            border-color: var(--sm-primary) !important;
            color: var(--sm-primary) !important;
            background: var(--sm-primary-light) !important;
        }

        .swagger-ui .btn.execute {
            background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
            color: var(--sm-white) !important;
            border: none !important;
            box-shadow: 0 4px 12px -2px rgba(79, 70, 229, 0.4) !important;
            font-weight: 700 !important;
        }

        .swagger-ui .btn.execute:hover {
            background: linear-gradient(135deg, #4338ca 0%, #4f46e5 100%) !important;
            transform: translateY(-1px);
            box-shadow: 0 6px 16px -2px rgba(79, 70, 229, 0.5) !important;
        }

        .swagger-ui .btn.cancel {
            background: var(--bg-card) !important;
            border: 1px solid #fecdd3 !important;
            color: #e11d48 !important;
        }

        .swagger-ui .btn.btn-clear {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-muted) !important;
        }

        /* Tables & Parameters */
        .swagger-ui table thead tr th,
        .swagger-ui table thead tr td {
            font-family: var(--sm-font-sans) !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            color: var(--text-muted) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            border-bottom: 2px solid var(--border-color) !important;
            background: transparent !important;
        }

        .swagger-ui table tbody tr td {
            font-family: var(--sm-font-sans) !important;
            font-size: 13px !important;
            color: var(--text-main) !important;
            border-bottom: 1px solid var(--border-color) !important;
            background: transparent !important;
        }

        .swagger-ui .parameter__name {
            font-family: var(--sm-font-mono) !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            color: var(--text-main) !important;
        }

        .swagger-ui .parameter__type {
            font-family: var(--sm-font-mono) !important;
            font-size: 11px !important;
            color: var(--sm-primary) !important;
            font-weight: 600 !important;
        }

        /* Inputs, Selects & Textareas */
        .swagger-ui input[type="text"],
        .swagger-ui input[type="password"],
        .swagger-ui select,
        .swagger-ui textarea {
            border: 1px solid var(--input-border) !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            font-family: var(--sm-font-mono) !important;
            font-size: 12px !important;
            color: var(--text-main) !important;
            background: var(--input-bg) !important;
            transition: all 0.2s ease !important;
        }

        .swagger-ui input[type="text"]:focus,
        .swagger-ui select:focus,
        .swagger-ui textarea:focus {
            outline: none !important;
            border-color: var(--sm-primary) !important;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2) !important;
        }

        /* Dark Editor Code & JSON Blocks */
        .swagger-ui .highlight-code,
        .swagger-ui pre,
        .swagger-ui .microlight,
        .swagger-ui pre.microlight,
        .swagger-ui .example__code {
            background-color: #0f172a !important;
            color: #e2e8f0 !important;
            border-radius: 10px !important;
            padding: 16px !important;
            font-family: var(--sm-font-mono) !important;
            font-size: 12px !important;
            line-height: 1.55 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3) !important;
            overflow-x: auto !important;
        }

        .swagger-ui pre code {
            font-family: var(--sm-font-mono) !important;
            color: #e2e8f0 !important;
        }

        /* Responses Container */
        .swagger-ui .responses-inner {
            padding: 16px 0;
        }

        .swagger-ui .responses-table {
            border-radius: var(--sm-card-radius);
            overflow: hidden;
            border: 1px solid var(--border-color);
            background: var(--bg-card);
        }

        .swagger-ui .response-col_status {
            font-family: var(--sm-font-mono) !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            color: var(--text-main) !important;
        }

        /* Schemas / Models Accordion */
        .swagger-ui section.models {
            border: 1px solid var(--border-color) !important;
            border-radius: var(--sm-card-radius) !important;
            background: var(--bg-card) !important;
            box-shadow: var(--shadow-card) !important;
            margin-top: 36px !important;
        }

        .swagger-ui section.models h4 {
            font-family: var(--sm-font-sans) !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            color: var(--text-main) !important;
            padding: 16px 22px !important;
            border-bottom: 1px solid var(--border-color) !important;
        }

        .swagger-ui section.models .model-box {
            background: var(--bg-card-subtle) !important;
            border-radius: 8px !important;
            padding: 12px !important;
            margin: 8px 0 !important;
        }

        .swagger-ui .model-title {
            font-family: var(--sm-font-mono) !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            color: var(--text-main) !important;
        }

        /* Modal Dialog (Authorize popup) */
        .swagger-ui .dialog-ux .modal-ux {
            border-radius: 16px !important;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.3) !important;
            border: 1px solid var(--border-color) !important;
            background: var(--bg-card) !important;
            overflow: hidden;
        }

        .swagger-ui .dialog-ux .modal-ux-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            color: #ffffff;
            padding: 18px 24px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .swagger-ui .dialog-ux .modal-ux-header h3 {
            color: #ffffff !important;
            font-family: var(--sm-font-sans) !important;
            font-weight: 700 !important;
            font-size: 16px !important;
        }

        .swagger-ui .dialog-ux .modal-ux-content {
            padding: 24px !important;
            background: var(--bg-card);
            color: var(--text-main);
        }

        /* Scrollbars */
        ::-webkit-scrollbar {
            width: 7px;
            height: 7px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-page);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--sm-slate-400);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--sm-slate-500);
        }

        /* Responsive Breakpoints */
        @media (max-width: 768px) {
            .studymate-brand-header {
                padding: 18px 16px;
            }
            .studymate-brand-container {
                flex-direction: column;
                align-items: flex-start;
            }
            .swagger-ui .wrapper {
                padding: 16px;
            }
            .swagger-ui .opblock .opblock-summary {
                flex-wrap: wrap;
                gap: 8px;
            }
            .swagger-ui .opblock .opblock-summary-description {
                margin-left: 0;
                width: 100%;
                padding-left: 14px;
            }
        }
    </style>
</head>
<body>

    <!-- StudyMate AI SaaS Top Branding Header -->
    <header class="studymate-brand-header">
        <div class="studymate-brand-container">
            <div class="studymate-brand-left">
                <div class="studymate-brand-logo">🤖</div>
                <div class="studymate-brand-titles">
                    <h1>
                        StudyMate AI
                        <span class="badge-pill">API v1.0</span>
                    </h1>
                    <p class="subtitle">AI-Powered Study Assistant API</p>
                    <p class="description">Document-grounded AI APIs for document processing, RAG chat, summaries, quizzes, flashcards and learning progress.</p>
                </div>
            </div>

            <div class="studymate-brand-actions">
                <span class="badge-status">
                    <span class="status-dot"></span>
                    API Operational
                </span>
                <button id="themeToggleBtn" class="btn-theme-toggle" onclick="toggleDocsTheme()" title="Toggle Light/Dark Theme">
                    <span id="themeToggleIcon">🌙</span>
                    <span id="themeToggleText">Dark Mode</span>
                </button>
                <a href="/" class="btn-header-link" title="Open StudyMate AI Web App">🖥️ Open Web App</a>
                <a href="/openapi.json" target="_blank" class="btn-header-link" title="View OpenAPI Specification">📋 OpenAPI JSON</a>
            </div>
        </div>
    </header>

    <!-- Swagger UI Mount Point -->
    <div id="swagger-ui"></div>

    <!-- Swagger UI Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>

    <script>
        // Theme Toggle Persistence
        function initTheme() {
            const savedTheme = localStorage.getItem('studymate_docs_theme');
            if (savedTheme === 'dark') {
                document.body.classList.add('dark');
                document.getElementById('themeToggleIcon').textContent = '☀️';
                document.getElementById('themeToggleText').textContent = 'Light Mode';
            } else {
                document.body.classList.remove('dark');
                document.getElementById('themeToggleIcon').textContent = '🌙';
                document.getElementById('themeToggleText').textContent = 'Dark Mode';
            }
        }

        function toggleDocsTheme() {
            const isDark = document.body.classList.toggle('dark');
            if (isDark) {
                localStorage.setItem('studymate_docs_theme', 'dark');
                document.getElementById('themeToggleIcon').textContent = '☀️';
                document.getElementById('themeToggleText').textContent = 'Light Mode';
            } else {
                localStorage.setItem('studymate_docs_theme', 'light');
                document.getElementById('themeToggleIcon').textContent = '🌙';
                document.getElementById('themeToggleText').textContent = 'Dark Mode';
            }
        }

        window.onload = function() {
            initTheme();
            
            window.ui = SwaggerUIBundle({
                url: '/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                filter: true, // Live instant search across endpoints
                docExpansion: 'list',
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                displayRequestDuration: true,
                persistAuthorization: true, // Retains Bearer JWT token across page reloads
                syntaxHighlight: {
                    theme: 'monokai'
                },
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "BaseLayout"
            });
        };
    </script>
</body>
</html>"""
