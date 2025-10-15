#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xsukax Directory Tree Comparison Tool
A single-file web application for comparing two directory trees in detail.
"""

import os
import sys
import hashlib
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from tkinter import Tk, filedialog

# Ensure proper encoding for Windows
if sys.platform == 'win32':
    import locale
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>xsukax Directory Tree Comparison</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif; background: #0d1117; color: #c9d1d9; line-height: 1.5; }
        .container { max-width: 1600px; margin: 0 auto; padding: 20px; }
        .header { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px; margin-bottom: 20px; }
        h1 { font-size: 28px; font-weight: 600; margin-bottom: 8px; color: #58a6ff; display: flex; align-items: center; gap: 12px; }
        .subtitle { font-size: 14px; color: #8b949e; margin-bottom: 20px; }
        .input-section { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .input-group { display: flex; flex-direction: column; gap: 8px; }
        label { font-size: 14px; font-weight: 600; color: #f0f6fc; }
        .path-input-wrapper { display: flex; gap: 8px; }
        input[type="text"] { flex: 1; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 8px 12px; color: #c9d1d9; font-size: 14px; transition: border-color 0.2s; font-family: 'SF Mono', Monaco, Consolas, monospace; }
        input[type="text"]:focus { outline: none; border-color: #58a6ff; }
        input[type="text"]::placeholder { color: #6e7681; }
        .browse-btn { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; padding: 8px 16px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
        .browse-btn:hover { background: #30363d; border-color: #58a6ff; }
        .browse-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .help-text { font-size: 12px; color: #6e7681; margin-top: 4px; }
        .button-group { display: flex; gap: 10px; margin-top: 16px; }
        button { background: #238636; color: #fff; border: none; border-radius: 6px; padding: 10px 20px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #2ea043; }
        button:disabled { background: #21262d; color: #484f58; cursor: not-allowed; }
        .secondary-btn { background: #21262d; color: #c9d1d9; }
        .secondary-btn:hover { background: #30363d; }
        .message-bar { padding: 12px 16px; border-radius: 6px; margin-bottom: 16px; display: none; align-items: center; gap: 10px; font-size: 14px; animation: slideDown 0.3s ease; }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        .message-bar.show { display: flex; }
        .message-bar.error { background: #4c1e1e; border: 1px solid #f85149; color: #ffa198; }
        .message-bar.success { background: #1a472a; border: 1px solid #3fb950; color: #7ee787; }
        .message-bar.info { background: #1f3a5f; border: 1px solid #58a6ff; color: #79c0ff; }
        .message-icon { font-size: 18px; }
        .message-close { margin-left: auto; cursor: pointer; font-size: 20px; opacity: 0.7; }
        .message-close:hover { opacity: 1; }
        .comparison-panel { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px; min-height: 400px; }
        .legend { display: flex; gap: 24px; margin-bottom: 20px; padding: 12px 16px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; justify-content: center; }
        .legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 500; }
        .legend-dot { width: 12px; height: 12px; border-radius: 50%; border: 2px solid currentColor; }
        .legend-same { color: #3fb950; }
        .legend-different { color: #f85149; }
        .legend-missing { color: #8b949e; }
        .main-content { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        .tree-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .tree-side { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 16px; max-height: 70vh; overflow-y: auto; }
        .tree-side h3 { font-size: 16px; font-weight: 600; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #21262d; color: #f0f6fc; }
        .tree-item { padding: 2px 0; }
        .tree-item-content { display: flex; align-items: center; padding: 6px 10px; border-radius: 4px; transition: background 0.1s; cursor: pointer; user-select: none; }
        .tree-item-content:hover { background: #161b22; }
        .tree-item-content.selected { background: #1f6feb; }
        .tree-item-icon { width: 18px; margin-right: 8px; flex-shrink: 0; font-size: 16px; }
        .tree-item-name { flex: 1; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .tree-item-children { margin-left: 24px; }
        .folder-icon::before { content: '📁'; }
        .file-icon::before { content: '📄'; }
        .expanded .folder-icon::before { content: '📂'; }
        .status-same { color: #3fb950; border-left: 3px solid #3fb950; }
        .status-different { color: #f85149; border-left: 3px solid #f85149; font-weight: 500; }
        .status-missing { color: #8b949e; opacity: 0.6; border-left: 3px solid #8b949e; }
        .details-panel { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 16px; max-height: 70vh; overflow-y: auto; position: sticky; top: 20px; }
        .details-panel h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid #21262d; color: #f0f6fc; }
        .detail-section { margin-bottom: 20px; }
        .detail-section-title { font-size: 13px; font-weight: 600; color: #58a6ff; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
        .detail-item { background: #161b22; border: 1px solid #21262d; border-radius: 6px; padding: 12px; margin-bottom: 12px; }
        .detail-row { display: flex; justify-content: space-between; margin-bottom: 8px; }
        .detail-row:last-child { margin-bottom: 0; }
        .detail-label { font-size: 12px; color: #8b949e; }
        .detail-value { font-size: 13px; color: #c9d1d9; font-family: 'SF Mono', Monaco, Consolas, monospace; word-break: break-all; font-weight: 500; }
        .detail-hash { font-size: 11px; color: #8b949e; margin-top: 8px; word-break: break-all; }
        .status-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
        .badge-same { background: #1a472a; color: #3fb950; }
        .badge-different { background: #4c1e1e; color: #f85149; }
        .badge-missing { background: #21262d; color: #8b949e; }
        .loading { display: none; text-align: center; padding: 60px; color: #8b949e; }
        .loading.active { display: block; }
        .spinner { border: 3px solid #21262d; border-top: 3px solid #58a6ff; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 0 auto 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .empty-state { text-align: center; padding: 60px 20px; color: #8b949e; }
        .empty-state-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
        ::-webkit-scrollbar { width: 10px; height: 10px; }
        ::-webkit-scrollbar-track { background: #0d1117; }
        ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 5px; }
        ::-webkit-scrollbar-thumb:hover { background: #484f58; }
        .comparison-summary { display: flex; gap: 16px; margin-bottom: 20px; }
        .summary-card { flex: 1; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 12px 16px; text-align: center; }
        .summary-value { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
        .summary-label { font-size: 12px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗂️ xsukax Directory Tree Comparison</h1>
            <div class="subtitle">Compare directory structures and file contents with detailed analysis</div>
            
            <div id="message-container"></div>
            
            <div class="input-section">
                <div class="input-group">
                    <label for="dir1">Directory 1 (Left)</label>
                    <div class="path-input-wrapper">
                        <input type="text" id="dir1" placeholder="C:\\Users\\Username\\Documents\\Folder1">
                        <button class="browse-btn" onclick="browseFolder('dir1')">📁 Browse</button>
                    </div>
                    <div class="help-text">💡 Enter the full path or click Browse to select folder</div>
                </div>
                <div class="input-group">
                    <label for="dir2">Directory 2 (Right)</label>
                    <div class="path-input-wrapper">
                        <input type="text" id="dir2" placeholder="C:\\Users\\Username\\Documents\\Folder2">
                        <button class="browse-btn" onclick="browseFolder('dir2')">📁 Browse</button>
                    </div>
                    <div class="help-text">💡 Enter the full path or click Browse to select folder</div>
                </div>
            </div>
            
            <div class="button-group">
                <button onclick="compareDirectories()" id="compareBtn">🔍 Compare Directories</button>
                <button class="secondary-btn" onclick="clearResults()">Clear Results</button>
            </div>
        </div>

        <div class="comparison-panel">
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div style="font-size: 16px; font-weight: 500;">Analyzing directories...</div>
                <div style="font-size: 13px; margin-top: 8px; opacity: 0.7;">This may take a moment for large directories</div>
            </div>
            
            <div id="results" style="display: none;">
                <div class="legend">
                    <div class="legend-item legend-same">
                        <div class="legend-dot"></div>
                        <span>Identical</span>
                    </div>
                    <div class="legend-item legend-different">
                        <div class="legend-dot"></div>
                        <span>Different</span>
                    </div>
                    <div class="legend-item legend-missing">
                        <div class="legend-dot"></div>
                        <span>Missing</span>
                    </div>
                </div>

                <div class="comparison-summary" id="summary"></div>
                
                <div class="main-content">
                    <div class="tree-container">
                        <div class="tree-side">
                            <h3 id="tree1-title">Directory 1</h3>
                            <div id="tree1"></div>
                        </div>
                        <div class="tree-side">
                            <h3 id="tree2-title">Directory 2</h3>
                            <div id="tree2"></div>
                        </div>
                    </div>

                    <div class="details-panel">
                        <h3>File Details</h3>
                        <div id="details-content">
                            <div class="empty-state">
                                <div class="empty-state-icon">📋</div>
                                <div>Select a file to view details</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let comparisonData = null;
        let selectedPath = null;

        function showMessage(message, type = 'info') {
            const container = document.getElementById('message-container');
            const icons = { error: '❌', success: '✅', info: 'ℹ️' };
            
            const messageBar = document.createElement('div');
            messageBar.className = `message-bar ${type} show`;
            messageBar.innerHTML = `
                <span class="message-icon">${icons[type]}</span>
                <span>${message}</span>
                <span class="message-close" onclick="this.parentElement.remove()">×</span>
            `;
            
            container.innerHTML = '';
            container.appendChild(messageBar);
            
            setTimeout(() => {
                if (messageBar.parentElement) {
                    messageBar.remove();
                }
            }, 5000);
        }

        async function browseFolder(inputId) {
            try {
                const response = await fetch('/browse_folder', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json; charset=utf-8' }
                });

                const data = await response.json();

                if (response.ok && data.path) {
                    document.getElementById(inputId).value = data.path;
                }
            } catch (error) {
                console.error('Browser error:', error);
            }
        }

        async function compareDirectories() {
            const dir1 = document.getElementById('dir1').value.trim();
            const dir2 = document.getElementById('dir2').value.trim();

            if (!dir1 || !dir2) {
                showMessage('Please enter both directory paths.', 'error');
                return;
            }

            document.getElementById('loading').classList.add('active');
            document.getElementById('results').style.display = 'none';
            document.getElementById('compareBtn').disabled = true;

            try {
                const response = await fetch('/compare', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json; charset=utf-8' },
                    body: JSON.stringify({ dir1, dir2 })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Comparison failed');
                }

                comparisonData = data;
                renderResults(data);
                document.getElementById('results').style.display = 'block';
                showMessage('Directories compared successfully!', 'success');
            } catch (error) {
                showMessage(error.message, 'error');
            } finally {
                document.getElementById('loading').classList.remove('active');
                document.getElementById('compareBtn').disabled = false;
            }
        }

        function renderResults(data) {
            document.getElementById('tree1-title').textContent = data.dir1;
            document.getElementById('tree2-title').textContent = data.dir2;
            document.getElementById('tree1').innerHTML = renderTree(data.tree1, 'left', '');
            document.getElementById('tree2').innerHTML = renderTree(data.tree2, 'right', '');
            
            const stats = calculateStats(data.tree1, data.tree2);
            renderSummary(stats);
            
            selectedPath = null;
            document.getElementById('details-content').innerHTML = '<div class="empty-state"><div class="empty-state-icon">📋</div><div>Select a file to view details</div></div>';
        }

        function calculateStats(tree1, tree2) {
            let stats = { same: 0, different: 0, missing: 0 };
            
            function count(node) {
                if (!node) return;
                if (node.type === 'file') {
                    if (node.status === 'same') stats.same++;
                    else if (node.status === 'different') stats.different++;
                    else if (node.status === 'missing') stats.missing++;
                }
                if (node.children) {
                    node.children.forEach(count);
                }
            }
            
            count(tree1);
            count(tree2);
            
            return stats;
        }

        function renderSummary(stats) {
            const html = `
                <div class="summary-card">
                    <div class="summary-value legend-same">${stats.same}</div>
                    <div class="summary-label">Identical Files</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value legend-different">${stats.different}</div>
                    <div class="summary-label">Different Files</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value legend-missing">${stats.missing}</div>
                    <div class="summary-label">Missing Files</div>
                </div>
            `;
            document.getElementById('summary').innerHTML = html;
        }

        function renderTree(node, side, parentPath) {
            if (!node) return '<div class="status-missing">Directory not found or empty</div>';

            const currentPath = parentPath ? `${parentPath}/${node.name}` : node.name;
            const isFolder = node.type === 'folder';
            const statusClass = node.status ? `status-${node.status}` : '';
            
            const safeCurrentPath = currentPath.replace(/'/g, "\\'");
            
            let html = '<div class="tree-item">';
            html += `<div class="tree-item-content ${statusClass}" data-path="${safeCurrentPath}" data-side="${side}" onclick="handleItemClick(event, '${side}', '${safeCurrentPath}', ${isFolder})">`;
            html += `<span class="tree-item-icon ${isFolder ? 'folder-icon' : 'file-icon'}"></span>`;
            html += `<span class="tree-item-name">${node.name}</span>`;
            html += '</div>';

            if (isFolder && node.children && node.children.length > 0) {
                html += '<div class="tree-item-children">';
                node.children.forEach(child => {
                    html += renderTree(child, side, currentPath);
                });
                html += '</div>';
            }

            html += '</div>';
            return html;
        }

        function handleItemClick(event, side, path, isFolder) {
            if (isFolder) {
                const element = event.target.closest('.tree-item');
                element.classList.toggle('expanded');
            } else {
                document.querySelectorAll('.tree-item-content.selected').forEach(el => {
                    el.classList.remove('selected');
                });
                event.target.closest('.tree-item-content').classList.add('selected');
                
                selectedPath = path;
                showFileDetails(path);
            }
        }

        function showFileDetails(path) {
            const pathParts = path.split('/').filter(p => p);
            const relativePath = pathParts.slice(1).join('/');
            
            const file1 = findFileByRelativePath(comparisonData.tree1, relativePath);
            const file2 = findFileByRelativePath(comparisonData.tree2, relativePath);

            if (!file1 && !file2) {
                document.getElementById('details-content').innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div><div>Could not find file in tree</div></div>';
                return;
            }

            let html = '';
            
            html += '<div class="detail-section">';
            html += `<div class="detail-section-title">📁 ${comparisonData.dir1}</div>`;
            html += '<div class="detail-item">';
            if (file1 && file1.type === 'file') {
                html += `<div class="detail-row"><span class="detail-label">Status</span><span class="status-badge badge-${file1.status}">${file1.status}</span></div>`;
                html += `<div class="detail-row"><span class="detail-label">Size</span><span class="detail-value">${formatBytes(file1.size)}</span></div>`;
                html += `<div class="detail-row"><span class="detail-label">Size on Disk</span><span class="detail-value">${formatBytes(file1.size_on_disk)}</span></div>`;
                html += `<div class="detail-row"><span class="detail-label">Created</span><span class="detail-value">${formatDate(file1.created)}</span></div>`;
                html += `<div class="detail-row"><span class="detail-label">Modified</span><span class="detail-value">${formatDate(file1.modified)}</span></div>`;
                html += `<div class="detail-row"><span class="detail-label">Accessed</span><span class="detail-value">${formatDate(file1.accessed)}</span></div>`;
                if (file1.md5) html += `<div class="detail-hash">MD5: ${file1.md5}</div>`;
            } else {
                html += '<div class="detail-value status-missing">❌ File not found in this directory</div>';
            }
            html += '</div></div>';

            html += '<div class="detail-section">';
            html += `<div class="detail-section-title">📁 ${comparisonData.dir2}</div>`;
            html += '<div class="detail-item">';
            if (file2 && file2.type === 'file') {
                html += `<div class="detail-row"><span class="detail-label">Status</span><span class="status-badge badge-${file2.status}">${file2.status}</span></div>`;
                html += `<div class="detail-row"><span class="detail-label">Size</span><span class="detail-value">${formatBytes(file2.size)}</span></div>`;
                html += `<div class="detail-row"><span class="detail-label">Size on Disk</span><span class="detail-value">${formatBytes(file2.size_on_disk)}</span></div>`;
                html += `<div class="detail-row"><span class="detail-label">Created</span><span class="detail-value">${formatDate(file2.created)}</span></div>`;
                html += `<div class="detail-row"><span class="detail-label">Modified</span><span class="detail-value">${formatDate(file2.modified)}</span></div>`;
                html += `<div class="detail-row"><span class="detail-label">Accessed</span><span class="detail-value">${formatDate(file2.accessed)}</span></div>`;
                if (file2.md5) html += `<div class="detail-hash">MD5: ${file2.md5}</div>`;
            } else {
                html += '<div class="detail-value status-missing">❌ File not found in this directory</div>';
            }
            html += '</div></div>';

            document.getElementById('details-content').innerHTML = html;
        }

        function findFileByRelativePath(rootNode, relativePath) {
            if (!rootNode) return null;
            
            if (!relativePath || relativePath === '') {
                return rootNode;
            }
            
            const parts = relativePath.split('/').filter(p => p);
            let current = rootNode;
            
            for (let i = 0; i < parts.length; i++) {
                if (!current.children) {
                    return null;
                }
                
                current = current.children.find(child => child.name === parts[i]);
                
                if (!current) {
                    return null;
                }
            }
            
            return current;
        }

        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        function formatDate(timestamp) {
            if (!timestamp) return 'N/A';
            return new Date(timestamp * 1000).toLocaleString();
        }

        function clearResults() {
            document.getElementById('dir1').value = '';
            document.getElementById('dir2').value = '';
            document.getElementById('results').style.display = 'none';
            document.getElementById('message-container').innerHTML = '';
            comparisonData = null;
            selectedPath = null;
        }
    </script>
</body>
</html>
"""


def normalize_path(path_str):
    """Normalize path to handle Unicode characters properly on Windows."""
    try:
        path = Path(path_str)
        return str(path.resolve())
    except Exception:
        return path_str


def get_file_info(path):
    """Get detailed file information including metadata and hash."""
    try:
        if sys.platform == 'win32':
            path = os.path.normpath(path)
        
        stat = os.stat(path)
        info = {
            'size': stat.st_size,
            'size_on_disk': stat.st_blocks * 512 if hasattr(stat, 'st_blocks') else stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
        }
        
        if os.path.isfile(path):
            md5_hash = hashlib.md5()
            try:
                with open(path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b''):
                        md5_hash.update(chunk)
                info['md5'] = md5_hash.hexdigest()
            except Exception:
                info['md5'] = None
        
        return info
    except Exception as e:
        print(f"Error getting file info for {path}: {e}")
        return None


def build_tree(root_path):
    """Build a tree structure of the directory with file information."""
    try:
        if sys.platform == 'win32':
            root_path = os.path.normpath(root_path)
        
        if not os.path.exists(root_path):
            return None
        
        path_obj = Path(root_path)
        name = path_obj.name if path_obj.name else str(path_obj)
        
        node = {
            'name': name,
            'type': 'folder' if os.path.isdir(root_path) else 'file',
            'path': str(root_path)
        }
        
        if os.path.isdir(root_path):
            node['children'] = []
            try:
                entries = sorted(os.listdir(root_path))
                for entry in entries:
                    child_path = os.path.join(root_path, entry)
                    child_node = build_tree(child_path)
                    if child_node:
                        node['children'].append(child_node)
            except PermissionError:
                pass
            except Exception as e:
                print(f"Error reading directory {root_path}: {e}")
        else:
            info = get_file_info(root_path)
            if info:
                node.update(info)
        
        return node
    except Exception as e:
        print(f"Error building tree for {root_path}: {e}")
        return None


def compare_nodes(node1, node2):
    """Compare two nodes and add status information."""
    if not node1 and not node2:
        return None, None
    
    if not node1:
        node2_copy = node2.copy()
        node2_copy['status'] = 'missing'
        if node2_copy.get('type') == 'folder' and 'children' in node2_copy:
            node2_copy['children'] = [compare_nodes(None, c)[1] for c in node2_copy['children']]
        return None, node2_copy
    
    if not node2:
        node1_copy = node1.copy()
        node1_copy['status'] = 'missing'
        if node1_copy.get('type') == 'folder' and 'children' in node1_copy:
            node1_copy['children'] = [compare_nodes(c, None)[0] for c in node1_copy['children']]
        return node1_copy, None
    
    node1_copy = node1.copy()
    node2_copy = node2.copy()
    
    if node1.get('type') == 'file' and node2.get('type') == 'file':
        if node1.get('md5') and node2.get('md5'):
            if node1['md5'] == node2['md5']:
                node1_copy['status'] = 'same'
                node2_copy['status'] = 'same'
            else:
                node1_copy['status'] = 'different'
                node2_copy['status'] = 'different'
        else:
            node1_copy['status'] = 'different'
            node2_copy['status'] = 'different'
    elif node1.get('type') == 'folder' and node2.get('type') == 'folder':
        children1 = {c['name']: c for c in node1.get('children', [])}
        children2 = {c['name']: c for c in node2.get('children', [])}
        all_names = set(children1.keys()) | set(children2.keys())
        
        new_children1 = []
        new_children2 = []
        
        for name in sorted(all_names):
            c1, c2 = compare_nodes(children1.get(name), children2.get(name))
            if c1:
                new_children1.append(c1)
            if c2:
                new_children2.append(c2)
        
        node1_copy['children'] = new_children1
        node2_copy['children'] = new_children2
        node1_copy['status'] = 'same'
        node2_copy['status'] = 'same'
    else:
        node1_copy['status'] = 'different'
        node2_copy['status'] = 'different'
    
    return node1_copy, node2_copy


@app.route('/')
def index():
    """Render the main page."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/browse_folder', methods=['POST'])
def browse_folder():
    """Open folder browser dialog and return selected path."""
    try:
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        folder_path = filedialog.askdirectory(title='Select Folder')
        
        root.destroy()
        
        if folder_path:
            return jsonify({'path': folder_path})
        else:
            return jsonify({'error': 'No folder selected'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/compare', methods=['POST'])
def compare():
    """Compare two directories and return the tree structures."""
    try:
        data = request.get_json()
        dir1 = data.get('dir1', '').strip()
        dir2 = data.get('dir2', '').strip()
        
        if not dir1 or not dir2:
            return jsonify({'error': 'Both directory paths are required'}), 400
        
        dir1 = normalize_path(dir1)
        dir2 = normalize_path(dir2)
        
        if not os.path.exists(dir1):
            return jsonify({'error': f'Directory 1 does not exist: {dir1}'}), 400
        
        if not os.path.exists(dir2):
            return jsonify({'error': f'Directory 2 does not exist: {dir2}'}), 400
        
        tree1 = build_tree(dir1)
        tree2 = build_tree(dir2)
        
        if not tree1 and not tree2:
            return jsonify({'error': 'Both directories are empty or inaccessible'}), 400
        
        tree1_compared, tree2_compared = compare_nodes(tree1, tree2)
        
        return jsonify({
            'dir1': dir1,
            'dir2': dir2,
            'tree1': tree1_compared,
            'tree2': tree2_compared
        })
    
    except Exception as e:
        import traceback
        print(f"Error during comparison: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 70)
    print("xsukax Directory Tree Comparison Tool")
    print("=" * 70)
    print("\nStarting server on http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server\n")
    app.run(debug=True, host='127.0.0.1', port=5000)