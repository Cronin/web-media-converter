#!/usr/bin/env python3
"""
Web Media Converter - Beautiful Local Media Conversion Tool
Convert videos to WebM and images to WebP with multiple stunning UI themes
"""

from flask import Flask, request, send_file, jsonify, render_template_string
import os
import subprocess
from pathlib import Path
import tempfile
import base64
from werkzeug.utils import secure_filename
import json
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size per file

UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg', '.3gp', '.webm'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.svg', '.webp'}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Media Converter - Beautiful Local Conversion</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        /* Dark Theme (Default) */
        body.dark-theme {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
        }
        
        body.dark-theme .container {
            background: linear-gradient(135deg, #2a2a2a 0%, #3a3a3a 100%);
            color: #ffffff;
            box-shadow: 0 20px 60px rgba(0,0,0,0.8),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        body.dark-theme .drop-zone {
            background: #3a3a3a;
            border-color: #808080;
        }
        
        body.dark-theme .drop-zone:hover {
            background: #4a4a4a;
            border-color: #a0a0a0;
        }
        
        body.dark-theme .quality-control {
            background: #3a3a3a;
            border-color: #606060;
        }
        
        body.dark-theme .quality-value {
            background: #4a4a4a;
            color: #ffffff;
            border-color: #707070;
        }
        
        body.dark-theme .file-queue {
            background: #3a3a3a;
            border-color: #606060;
        }
        
        body.dark-theme .file-item {
            background: #4a4a4a;
            border-color: #707070;
        }
        
        body.dark-theme h1,
        body.dark-theme .drop-zone-text,
        body.dark-theme .file-name,
        body.dark-theme .size-value {
            color: #ffffff;
        }
        
        body.dark-theme .subtitle,
        body.dark-theme .drop-zone-hint,
        body.dark-theme .size-label {
            color: #b0b0b0;
        }
        
        body.dark-theme .format-tag {
            background: #4a4a4a;
            color: #ffffff;
            border-color: #707070;
        }
        
        body.dark-theme .supported-formats {
            background: #3a3a3a;
            border-color: #606060;
        }
        
        /* Glass Theme - Original Style with Mountain Background */
        body.glass-theme {
            background: url("https://images.unsplash.com/photo-1432251407527-504a6b4174a2?q=80&w=1480&auto=format&fit=crop&ixlib=rb-4.1.0") center center;
            background-size: cover;
            animation: moveBackground 60s linear infinite;
        }
        
        @keyframes moveBackground {
            from { background-position: 0% 0%; }
            to { background-position: 0% -1000%; }
        }
        
        body.glass-theme .container {
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        
        body.glass-theme .drop-zone {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        body.glass-theme .drop-zone:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.5);
        }
        
        body.glass-theme .quality-control {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        body.glass-theme .quality-value {
            background: rgba(255, 255, 255, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.4);
        }
        
        body.glass-theme .file-queue {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        body.glass-theme .file-item {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        body.glass-theme h1,
        body.glass-theme .drop-zone-text,
        body.glass-theme .file-name,
        body.glass-theme .size-value {
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        body.glass-theme .subtitle {
            color: rgba(255, 255, 255, 0.9);
        }
        
        body.glass-theme .drop-zone-hint,
        body.glass-theme .size-label {
            color: rgba(255, 255, 255, 0.8);
        }
        
        body.glass-theme .format-tag {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        body.glass-theme .supported-formats {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
        }
        
        body.glass-theme .download-btn {
            background: rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.4);
        }
        
        body.glass-theme .download-btn:hover {
            background: rgba(255, 255, 255, 0.4);
        }
        
        body.glass-theme .toggle-btn {
            color: rgba(255, 255, 255, 0.9);
        }
        
        body.glass-theme .toggle-btn:hover {
            color: white;
        }
        
        body.glass-theme .drop-zone-icon {
            color: rgba(255, 255, 255, 0.8);
        }
        
        /* Liquid Glass Theme - Abstract Colorful Background */
        body.liquid-theme {
            background: url("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2064&auto=format&fit=crop") center center;
            background-size: cover;
            animation: gradientShift 15s ease infinite;
        }
        
        @keyframes gradientShift {
            0%, 100% { filter: hue-rotate(0deg); }
            50% { filter: hue-rotate(180deg); }
        }
        
        body.liquid-theme .container {
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.1) 0%, 
                rgba(255, 255, 255, 0.05) 100%);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37),
                        inset 0 1px 0 0 rgba(255, 255, 255, 0.3),
                        inset 0 -1px 0 0 rgba(255, 255, 255, 0.1);
        }
        
        body.liquid-theme .drop-zone {
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.07) 0%, 
                rgba(255, 255, 255, 0.03) 100%);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.2);
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        body.liquid-theme .drop-zone:hover {
            background: linear-gradient(135deg, 
                rgba(255, 255, 255, 0.15) 0%, 
                rgba(255, 255, 255, 0.08) 100%);
            border-color: rgba(255, 255, 255, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2),
                        inset 0 2px 4px rgba(255, 255, 255, 0.1);
        }
        
        body.liquid-theme h1,
        body.liquid-theme .drop-zone-text,
        body.liquid-theme .file-name,
        body.liquid-theme .size-value {
            color: white;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }
        
        body.liquid-theme .subtitle,
        body.liquid-theme .drop-zone-hint,
        body.liquid-theme .size-label {
            color: white;
        }
        
        body.liquid-theme .file-queue {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        body.liquid-theme .file-queue h2 {
            color: white;
        }
        
        body.liquid-theme .file-item {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
        }
        
        /* Celestial Theme - WebGL Shader Background */
        body.celestial-theme {
            background: #1a0033;
            position: relative;
            overflow: hidden;
        }
        
        #celestialCanvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        }
        
        body.celestial-theme::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at center, transparent 0%, rgba(26, 0, 51, 0.4) 100%);
            z-index: 0;
            pointer-events: none;
        }
        
        body.celestial-theme .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px) brightness(1.1);
            border: 2px solid transparent;
            background-image: 
                linear-gradient(rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.1)),
                linear-gradient(90deg, #4a4a4a, #6a6a6a, #8a8a8a);
            background-origin: border-box;
            background-clip: padding-box, border-box;
            box-shadow: 
                0 20px 60px rgba(100, 100, 100, 0.3),
                inset 0 0 0 1px rgba(255, 255, 255, 0.2);
        }
        
        body.celestial-theme .drop-zone {
            background: linear-gradient(135deg, 
                rgba(100, 100, 100, 0.1) 0%, 
                rgba(150, 150, 150, 0.1) 100%);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
            animation: celestialGlow 3s ease-in-out infinite;
        }
        
        @keyframes celestialGlow {
            0%, 100% {
                box-shadow: 0 0 20px rgba(100, 100, 100, 0.2);
            }
            50% {
                box-shadow: 0 0 30px rgba(150, 150, 150, 0.3);
            }
        }
        
        body.celestial-theme .drop-zone:hover {
            background: linear-gradient(135deg, 
                rgba(100, 100, 100, 0.2) 0%, 
                rgba(150, 150, 150, 0.2) 100%);
            transform: translateY(-2px) scale(1.02);
        }
        
        body.celestial-theme h1 {
            color: white !important;
            text-shadow: 0 2px 20px rgba(100, 100, 100, 0.5);
        }
        
        
        body.celestial-theme .subtitle,
        body.celestial-theme .drop-zone-text,
        body.celestial-theme .drop-zone-hint,
        body.celestial-theme .file-name,
        body.celestial-theme .size-value,
        body.celestial-theme .size-label {
            color: white;
            text-shadow: 0 2px 10px rgba(100, 100, 100, 0.3);
        }
        
        body.celestial-theme .file-queue {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        body.celestial-theme .file-queue h2 {
            color: white;
        }
        
        body.celestial-theme .file-item {
            background: linear-gradient(135deg, 
                rgba(100, 100, 100, 0.05) 0%, 
                rgba(150, 150, 150, 0.05) 100%);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
        }
        
        body.celestial-theme .quality-control {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        body.celestial-theme .format-tag {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        body.celestial-theme .supported-formats {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
        }
        
        body.celestial-theme .theme-btn {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        body.celestial-theme .theme-btn.active {
            background: linear-gradient(90deg, #4a4a4a, #6a6a6a);
            border-color: white;
            box-shadow: 0 4px 20px rgba(100, 100, 100, 0.4);
        }
        
        body.celestial-theme .convert-all-btn {
            background: linear-gradient(135deg, #4a4a4a 0%, #6a6a6a 100%);
            box-shadow: 0 4px 15px rgba(100, 100, 100, 0.4);
        }
        
        body.celestial-theme .download-link {
            background: linear-gradient(135deg, #4a4a4a 0%, #6a6a6a 100%);
        }
        
        body.celestial-theme .drop-zone-icon {
            color: rgba(255, 255, 255, 0.9);
        }
        
        body.celestial-theme .toggle-btn {
            color: rgba(255, 255, 255, 0.9);
        }
        
        /* Neumorphism Theme - Soft Background */
        body.neumorphism-theme {
            background: linear-gradient(145deg, #e6e6e6, #ffffff);
        }
        
        body.neumorphism-theme .container {
            background: #f0f0f0;
            box-shadow: 20px 20px 60px #cccccc,
                        -20px -20px 60px #ffffff;
            border: none;
        }
        
        body.neumorphism-theme .drop-zone {
            background: #f0f0f0;
            box-shadow: inset 5px 5px 10px #cccccc,
                        inset -5px -5px 10px #ffffff;
            border: none;
        }
        
        body.neumorphism-theme .drop-zone:hover {
            box-shadow: inset 8px 8px 16px #cccccc,
                        inset -8px -8px 16px #ffffff;
        }
        
        body.neumorphism-theme .theme-btn {
            background: #f0f0f0;
            box-shadow: 5px 5px 10px #cccccc,
                        -5px -5px 10px #ffffff;
            color: #333;
        }
        
        body.neumorphism-theme .theme-btn:hover {
            box-shadow: 8px 8px 16px #cccccc,
                        -8px -8px 16px #ffffff;
        }
        
        body.neumorphism-theme .theme-btn.active {
            box-shadow: inset 5px 5px 10px #cccccc,
                        inset -5px -5px 10px #ffffff;
        }
        
        body.neumorphism-theme .file-queue {
            background: #f0f0f0;
            box-shadow: inset 3px 3px 6px #cccccc,
                        inset -3px -3px 6px #ffffff;
            border: none;
        }
        
        body.neumorphism-theme .file-item {
            background: #f0f0f0;
            box-shadow: 3px 3px 6px #cccccc,
                        -3px -3px 6px #ffffff;
            border: none;
        }
        
        /* Theme Switcher */
        .theme-switcher {
            position: fixed;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 1000;
            flex-wrap: wrap;
            max-width: 300px;
            justify-content: flex-end;
        }
        
        .theme-btn {
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.9);
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .theme-btn:hover {
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }
        
        .theme-btn.active {
            background: linear-gradient(135deg, #5a5a5a 0%, #7a7a7a 100%);
            color: white;
            box-shadow: 0 4px 20px rgba(100, 100, 100, 0.4);
        }
        
        body.glass-theme .theme-btn,
        body.liquid-theme .theme-btn {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        body.glass-theme .theme-btn.active,
        body.liquid-theme .theme-btn.active {
            background: rgba(255, 255, 255, 0.4);
            border-color: white;
            box-shadow: 0 4px 20px rgba(255, 255, 255, 0.3);
        }
        
        body.dark-theme .theme-btn {
            background: #333;
            color: #e0e0e0;
        }
        
        body.dark-theme .theme-btn:hover {
            background: #444;
        }
        
        body.dark-theme .theme-btn.active {
            background: #666;
            color: white;
        }
        
        .container {
            background: white;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 700px;
            width: 100%;
            position: relative;
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #5a5a5a 0%, #7a7a7a 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        body.glass-theme h1,
        body.liquid-theme h1 {
            background: white;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 2px 10px rgba(255, 255, 255, 0.3);
        }
        
        body.dark-theme h1 {
            background: linear-gradient(135deg, #5a5a5a 0%, #7a7a7a 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        body.neumorphism-theme h1 {
            color: #333;
            background: none;
            -webkit-text-fill-color: #333;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1em;
            font-weight: 400;
        }
        
        .drop-zone {
            border: 3px dashed #999;
            border-radius: 16px;
            padding: 60px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: #fafafa;
            position: relative;
            overflow: hidden;
        }
        
        .drop-zone:hover {
            transform: scale(1.02);
        }
        
        .drop-zone.dragover {
            transform: scale(1.05);
            border-color: #6a6a6a;
            background: rgba(102, 126, 234, 0.1);
        }
        
        .drop-zone-icon {
            font-size: 3em;
            margin-bottom: 20px;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        input[type="file"] {
            display: none;
        }
        
        /* File Queue for Multiple Files */
        .file-queue {
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            display: none;
        }
        
        .file-queue.active {
            display: block;
        }
        
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
        }
        
        .file-item.processing {
            background: linear-gradient(90deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            animation: pulse 2s infinite;
        }
        
        .file-item.completed {
            background: linear-gradient(90deg, rgba(132, 250, 176, 0.1) 0%, rgba(143, 211, 244, 0.1) 100%);
        }
        
        .file-item.error {
            background: linear-gradient(90deg, rgba(240, 147, 251, 0.1) 0%, rgba(245, 87, 108, 0.1) 100%);
        }
        
        .file-info-row {
            display: flex;
            flex-direction: column;
            flex: 1;
        }
        
        .file-name-row {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .file-status {
            font-size: 0.85em;
            color: #666;
        }
        
        .file-size-info {
            font-size: 0.85em;
            color: #999;
            margin-top: 3px;
        }
        
        .download-link {
            padding: 6px 12px;
            background: linear-gradient(135deg, #5a5a5a 0%, #7a7a7a 100%);
            color: white;
            text-decoration: none;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .download-link:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .quality-control {
            margin-top: 25px;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
        }
        
        .quality-control.hidden {
            display: none;
        }
        
        .quality-slider {
            width: 100%;
            height: 8px;
            -webkit-appearance: none;
            appearance: none;
            background: #ddd;
            outline: none;
            border-radius: 5px;
            transition: all 0.3s;
        }
        
        .quality-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            background: linear-gradient(135deg, #5a5a5a 0%, #7a7a7a 100%);
            cursor: pointer;
            border-radius: 50%;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
        }
        
        .quality-slider::-webkit-slider-thumb:hover {
            transform: scale(1.2);
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.5);
        }
        
        .progress-container {
            margin-top: 20px;
            padding: 15px;
            border-radius: 12px;
            background: #f8f9fa;
            display: none;
        }
        
        .progress-container.active {
            display: block;
        }
        
        .overall-progress {
            margin-bottom: 10px;
            font-weight: 600;
            text-align: center;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4a4a4a, #6a6a6a);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 10px;
        }
        
        .convert-all-btn {
            display: block;
            width: 100%;
            margin-top: 20px;
            padding: 15px;
            background: linear-gradient(135deg, #5a5a5a 0%, #7a7a7a 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .convert-all-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
        }
        
        .convert-all-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .supported-formats {
            margin-top: 30px;
            padding: 20px;
            border-radius: 12px;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }
        
        .format-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
        
        .format-tag {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .format-tag:hover {
            transform: scale(1.05);
        }
        
        .toggle-btn {
            background: none;
            border: none;
            color: #6a6a6a;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 600;
            text-decoration: underline;
            padding: 5px;
            transition: all 0.3s ease;
        }
        
        .toggle-btn:hover {
            color: #7a7a7a;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.01); }
            100% { transform: scale(1); }
        }
    </style>
</head>
<body class="dark-theme">
    <div class="theme-switcher">
        <button class="theme-btn active" data-theme="dark">Dark</button>
        <button class="theme-btn" data-theme="glass">Glass</button>
        <button class="theme-btn" data-theme="liquid">Liquid</button>
        <button class="theme-btn" data-theme="celestial">Celestial</button>
        <button class="theme-btn" data-theme="neumorphism">Soft</button>
    </div>
    
    <div class="container">
        <h1>Media Converter</h1>
        <p class="subtitle">Convert multiple videos to WebM or images to WebP locally</p>
        
        <div class="drop-zone" id="dropZone">
            <div class="drop-zone-icon">⬆</div>
            <div class="drop-zone-text">Drag & drop your files here</div>
            <div class="drop-zone-hint">or click to browse (multiple files supported)</div>
            <input type="file" id="fileInput" accept="video/*,image/*" multiple>
        </div>
        
        <div class="quality-toggle">
            <button class="toggle-btn" id="qualityToggle">Advanced settings</button>
        </div>
        
        <div class="quality-control hidden" id="qualityControl">
            <div class="quality-label">
                <span>Quality reduction:</span>
                <span class="quality-value" id="qualityValue">30%</span>
            </div>
            <input type="range" class="quality-slider" id="qualitySlider" min="10" max="90" value="30" step="5">
            <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.8em; opacity: 0.7;">
                <span>Better quality</span>
                <span>Smaller file</span>
            </div>
        </div>
        
        <div class="file-queue" id="fileQueue"></div>
        
        <button class="convert-all-btn" id="convertAllBtn" style="display: none;">
            Convert All Files
        </button>
        
        <div class="progress-container" id="progressContainer">
            <div class="overall-progress" id="overallProgress">Processing 0 of 0 files</div>
            <div class="progress-bar">
                <div class="progress-fill" id="overallProgressFill"></div>
            </div>
        </div>
        
        <div class="supported-formats">
            <strong>Supported formats:</strong>
            <div class="format-list">
                <span class="format-tag">MP4 → WebM</span>
                <span class="format-tag">AVI → WebM</span>
                <span class="format-tag">MOV → WebM</span>
                <span class="format-tag">JPG → WebP</span>
                <span class="format-tag">PNG → WebP</span>
                <span class="format-tag">GIF → WebP</span>
            </div>
        </div>
    </div>
    
    <script>
        // Theme Management
        const themeButtons = document.querySelectorAll('.theme-btn');
        const body = document.body;
        
        // Load saved theme (default to dark)
        const savedTheme = localStorage.getItem('preferredTheme') || 'dark';
        setTheme(savedTheme);
        
        themeButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const theme = btn.dataset.theme;
                setTheme(theme);
                localStorage.setItem('preferredTheme', theme);
            });
        });
        
        function setTheme(theme) {
            // Remove all theme classes
            body.classList.remove('dark-theme', 'glass-theme', 'liquid-theme', 'celestial-theme', 'neumorphism-theme');
            
            // Add new theme class
            body.classList.add(`${theme}-theme`);
            
            // Update active button
            themeButtons.forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.theme === theme) {
                    btn.classList.add('active');
                }
            });
        }
        
        // Multiple File Upload Support
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const fileQueue = document.getElementById('fileQueue');
        const convertAllBtn = document.getElementById('convertAllBtn');
        const progressContainer = document.getElementById('progressContainer');
        const overallProgress = document.getElementById('overallProgress');
        const overallProgressFill = document.getElementById('overallProgressFill');
        const qualitySlider = document.getElementById('qualitySlider');
        const qualityValue = document.getElementById('qualityValue');
        const qualityControl = document.getElementById('qualityControl');
        const qualityToggle = document.getElementById('qualityToggle');
        
        let fileList = [];
        let processedCount = 0;
        let isProcessing = false;
        
        // Quality slider
        qualitySlider.addEventListener('input', (e) => {
            qualityValue.textContent = e.target.value + '%';
        });
        
        // Toggle quality control
        qualityToggle.addEventListener('click', () => {
            qualityControl.classList.toggle('hidden');
            qualityToggle.textContent = qualityControl.classList.contains('hidden') ? 
                'Advanced settings' : 'Hide settings';
        });
        
        // Click to upload
        dropZone.addEventListener('click', () => fileInput.click());
        
        // Drag and drop events
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            const files = Array.from(e.dataTransfer.files);
            handleFiles(files);
        });
        
        // File input change
        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            handleFiles(files);
        });
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        function handleFiles(files) {
            files.forEach(file => {
                const fileId = generateFileId();
                const fileObj = {
                    id: fileId,
                    file: file,
                    status: 'pending',
                    originalSize: file.size
                };
                fileList.push(fileObj);
                addFileToQueue(fileObj);
            });
            
            if (fileList.length > 0) {
                fileQueue.classList.add('active');
                convertAllBtn.style.display = 'block';
            }
        }
        
        function generateFileId() {
            return 'file-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        }
        
        function addFileToQueue(fileObj) {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.id = fileObj.id;
            
            fileItem.innerHTML = `
                <div class="file-info-row">
                    <div class="file-name-row">${fileObj.file.name}</div>
                    <div class="file-status">Ready to convert</div>
                    <div class="file-size-info">Size: ${formatFileSize(fileObj.originalSize)}</div>
                </div>
                <div class="file-action" id="action-${fileObj.id}"></div>
            `;
            
            fileQueue.appendChild(fileItem);
        }
        
        // Convert all files button
        convertAllBtn.addEventListener('click', async () => {
            if (isProcessing) return;
            
            isProcessing = true;
            processedCount = 0;
            convertAllBtn.disabled = true;
            progressContainer.classList.add('active');
            
            for (let i = 0; i < fileList.length; i++) {
                if (fileList[i].status === 'pending') {
                    await convertFile(fileList[i]);
                    processedCount++;
                    updateOverallProgress();
                }
            }
            
            isProcessing = false;
            convertAllBtn.disabled = false;
            convertAllBtn.textContent = 'All files converted!';
        });
        
        function updateOverallProgress() {
            const total = fileList.length;
            const percentage = (processedCount / total) * 100;
            overallProgress.textContent = `Processing ${processedCount} of ${total} files`;
            overallProgressFill.style.width = percentage + '%';
        }
        
        async function convertFile(fileObj) {
            const fileElement = document.getElementById(fileObj.id);
            const statusElement = fileElement.querySelector('.file-status');
            const actionElement = document.getElementById(`action-${fileObj.id}`);
            
            fileElement.classList.add('processing');
            statusElement.textContent = 'Converting...';
            
            const formData = new FormData();
            formData.append('file', fileObj.file);
            formData.append('quality', qualitySlider.value);
            
            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('Conversion failed');
                }
                
                const blob = await response.blob();
                const filename = response.headers.get('Content-Disposition').split('filename=')[1].replace(/"/g, '');
                const fileSizeHeader = response.headers.get('X-File-Size');
                const convertedSize = fileSizeHeader ? parseInt(fileSizeHeader) : blob.size;
                
                const url = URL.createObjectURL(blob);
                const reduction = ((fileObj.originalSize - convertedSize) / fileObj.originalSize * 100).toFixed(1);
                
                fileElement.classList.remove('processing');
                fileElement.classList.add('completed');
                statusElement.textContent = `Converted! Saved ${reduction}%`;
                actionElement.innerHTML = `<a href="${url}" download="${filename}" class="download-link">Download</a>`;
                
                // Auto-download
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
                
                fileObj.status = 'completed';
            } catch (error) {
                fileElement.classList.remove('processing');
                fileElement.classList.add('error');
                statusElement.textContent = 'Conversion failed';
                fileObj.status = 'error';
            }
        }
    </script>
    <!-- Celestial WebGL Shader Canvas -->
    <canvas id="celestialCanvas"></canvas>
    
    <script>
        // Celestial WebGL Shader Implementation
        (function() {
            let celestialCanvas = document.getElementById('celestialCanvas');
            if (!celestialCanvas) return;
            
            let gl = celestialCanvas.getContext('webgl') || celestialCanvas.getContext('experimental-webgl');
            if (!gl) return;
            
            // Vertex shader source
            const vertexShaderSource = `
                attribute vec2 a_position;
                void main() {
                    gl_Position = vec4(a_position, 0.0, 1.0);
                }
            `;
            
            // Fragment shader source - Celestial Ink effect
            const fragmentShaderSource = `
                precision highp float;
                uniform vec2 u_resolution;
                uniform float u_time;
                uniform vec2 u_mouse;
                
                float random(vec2 st) {
                    return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
                }
                
                float noise(vec2 p) {
                    vec2 i = floor(p);
                    vec2 f = fract(p);
                    vec2 u = f * f * (3.0 - 2.0 * f);
                    return mix(
                        mix(random(i), random(i + vec2(1.0, 0.0)), u.x),
                        mix(random(i + vec2(0.0, 1.0)), random(i + vec2(1.0, 1.0)), u.x),
                        u.y
                    );
                }
                
                float fbm(vec2 p) {
                    float v = 0.0;
                    float a = 0.5;
                    for (int i = 0; i < 6; i++) {
                        v += a * noise(p);
                        p *= 2.0;
                        a *= 0.5;
                    }
                    return v;
                }
                
                void main() {
                    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
                    vec2 mouse = (u_mouse - 0.5 * u_resolution.xy) / u_resolution.y;
                    float t = u_time * 0.1;
                    
                    // Ripple effect around mouse
                    float d = length(uv - mouse);
                    float ripple = 1.0 - smoothstep(0.0, 0.5, d);
                    
                    // Rotation
                    float angle = t * 0.5;
                    mat2 rot = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
                    vec2 p = rot * uv;
                    
                    // Ink patterns
                    float pattern = fbm(p * 3.0 + t);
                    pattern -= fbm(p * 6.0 - t * 0.5) * 0.3;
                    pattern += ripple * 0.3;
                    
                    // Add flowing waves
                    pattern += sin(uv.x * 5.0 + t * 2.0) * 0.1;
                    pattern += cos(uv.y * 3.0 - t * 1.5) * 0.1;
                    
                    // Color palette - grey to white with golden highlights
                    vec3 c1 = vec3(0.1, 0.1, 0.1);  // Deep grey
                    vec3 c2 = vec3(0.8, 0.2, 0.4);  // Pink
                    vec3 c3 = vec3(0.4, 0.4, 0.4);  // Mid grey
                    vec3 highlight = vec3(1.0, 0.9, 0.7);  // Golden
                    
                    // Mix colors based on pattern
                    vec3 color = mix(c1, c2, smoothstep(0.3, 0.5, pattern));
                    color = mix(color, c3, smoothstep(0.5, 0.7, pattern));
                    
                    // Add highlights
                    float hl = pow(smoothstep(0.6, 0.8, pattern), 2.0);
                    color = mix(color, highlight, hl * 0.5);
                    
                    // Add subtle glow
                    color += vec3(0.1, 0.05, 0.15) * (1.0 - length(uv));
                    
                    gl_FragColor = vec4(color, 1.0);
                }
            `;
            
            // Create shader function
            function createShader(gl, type, source) {
                const shader = gl.createShader(type);
                gl.shaderSource(shader, source);
                gl.compileShader(shader);
                if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                    console.error('Shader compilation error:', gl.getShaderInfoLog(shader));
                    gl.deleteShader(shader);
                    return null;
                }
                return shader;
            }
            
            // Create program function
            function createProgram(gl, vertexShader, fragmentShader) {
                const program = gl.createProgram();
                gl.attachShader(program, vertexShader);
                gl.attachShader(program, fragmentShader);
                gl.linkProgram(program);
                if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
                    console.error('Program linking error:', gl.getProgramInfoLog(program));
                    gl.deleteProgram(program);
                    return null;
                }
                return program;
            }
            
            // Initialize shaders
            const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
            const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);
            const program = createProgram(gl, vertexShader, fragmentShader);
            
            if (!program) return;
            
            // Get attribute and uniform locations
            const positionAttributeLocation = gl.getAttribLocation(program, 'a_position');
            const resolutionUniformLocation = gl.getUniformLocation(program, 'u_resolution');
            const timeUniformLocation = gl.getUniformLocation(program, 'u_time');
            const mouseUniformLocation = gl.getUniformLocation(program, 'u_mouse');
            
            // Create buffer for rectangle
            const positionBuffer = gl.createBuffer();
            gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
            gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
                -1, -1,
                1, -1,
                -1, 1,
                -1, 1,
                1, -1,
                1, 1,
            ]), gl.STATIC_DRAW);
            
            // Mouse position tracking
            let mouseX = window.innerWidth / 2;
            let mouseY = window.innerHeight / 2;
            
            document.addEventListener('mousemove', (e) => {
                mouseX = e.clientX;
                mouseY = e.clientY;
            });
            
            // Resize handler
            function resizeCanvas() {
                celestialCanvas.width = window.innerWidth;
                celestialCanvas.height = window.innerHeight;
                gl.viewport(0, 0, celestialCanvas.width, celestialCanvas.height);
            }
            
            window.addEventListener('resize', resizeCanvas);
            resizeCanvas();
            
            // Animation loop
            let startTime = Date.now();
            let animationId;
            
            function render() {
                // Only render if celestial theme is active
                if (!document.body.classList.contains('celestial-theme')) {
                    animationId = requestAnimationFrame(render);
                    return;
                }
                
                const currentTime = (Date.now() - startTime) / 1000;
                
                gl.clearColor(0, 0, 0, 0);
                gl.clear(gl.COLOR_BUFFER_BIT);
                
                gl.useProgram(program);
                
                // Set uniforms
                gl.uniform2f(resolutionUniformLocation, celestialCanvas.width, celestialCanvas.height);
                gl.uniform1f(timeUniformLocation, currentTime);
                gl.uniform2f(mouseUniformLocation, mouseX, celestialCanvas.height - mouseY);
                
                // Bind position buffer
                gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
                gl.enableVertexAttribArray(positionAttributeLocation);
                gl.vertexAttribPointer(positionAttributeLocation, 2, gl.FLOAT, false, 0, 0);
                
                // Draw
                gl.drawArrays(gl.TRIANGLES, 0, 6);
                
                animationId = requestAnimationFrame(render);
            }
            
            // Start animation
            render();
            
            // Show/hide canvas based on theme
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                        if (document.body.classList.contains('celestial-theme')) {
                            celestialCanvas.style.display = 'block';
                        } else {
                            celestialCanvas.style.display = 'none';
                        }
                    }
                });
            });
            
            observer.observe(document.body, {
                attributes: true,
                attributeFilter: ['class']
            });
            
            // Initial hide if not celestial theme
            if (!document.body.classList.contains('celestial-theme')) {
                celestialCanvas.style.display = 'none';
            }
        })();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get quality setting
    quality = int(request.form.get('quality', 30))
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    input_path = Path(UPLOAD_FOLDER) / f"{uuid.uuid4()}_{filename}"
    file.save(str(input_path))
    
    # Get original file size
    original_size = input_path.stat().st_size
    
    # Determine file type and output format
    file_ext = input_path.suffix.lower()
    
    try:
        if file_ext in ALLOWED_VIDEO_EXTENSIONS:
            # Convert video to WebM
            output_path = input_path.with_suffix('.webm')
            
            # Calculate CRF value based on quality reduction percentage
            crf = int(10 + (quality * 0.6))  # Maps 10-90% to CRF 16-64
            
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-c:v', 'libvpx-vp9',
                '-crf', str(crf),
                '-b:v', '0',
                '-cpu-used', '5',
                '-c:a', 'libopus',
                '-b:a', '128k',
                '-y',
                str(output_path)
            ]
            
        elif file_ext in ALLOWED_IMAGE_EXTENSIONS:
            # Convert image to WebP
            output_path = input_path.with_suffix('.webp')
            
            # Calculate quality value (inverse of reduction percentage)
            webp_quality = 100 - quality
            
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-c:v', 'libwebp',
                '-quality', str(webp_quality),
                '-preset', 'default',
                '-y',
                str(output_path)
            ]
        else:
            os.remove(input_path)
            return jsonify({'error': f'Unsupported file format: {file_ext}'}), 400
        
        # Run conversion
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            os.remove(input_path)
            if output_path.exists():
                os.remove(output_path)
            return jsonify({'error': 'Conversion failed'}), 500
        
        # Get converted file size
        converted_size = output_path.stat().st_size
        
        # Get output filename without UUID
        output_filename = Path(filename).stem + output_path.suffix
        
        # Send converted file
        response = send_file(
            str(output_path),
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/octet-stream'
        )
        
        # Add file size to response headers
        response.headers['X-File-Size'] = str(converted_size)
        
        # Clean up after sending
        @response.call_on_close
        def cleanup():
            try:
                os.remove(input_path)
                os.remove(output_path)
            except:
                pass
        
        return response
        
    except subprocess.TimeoutExpired:
        if input_path.exists():
            os.remove(input_path)
        if output_path.exists():
            os.remove(output_path)
        return jsonify({'error': 'Conversion timeout - file too large or complex'}), 500
    except Exception as e:
        if input_path.exists():
            os.remove(input_path)
        if 'output_path' in locals() and output_path.exists():
            os.remove(output_path)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Web Media Converter with Beautiful Themes")
    print("Running at: http://127.0.0.1:8080")
    print("Convert multiple media files locally with style!")
    print("Multiple file support enabled!")
    app.run(host='127.0.0.1', debug=True, port=8080, threaded=True)