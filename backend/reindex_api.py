@app.route('/api/reindex-folder', methods=['POST'])
def reindex_folder():
    """重新索引文件夹"""
    try:
        data = request.get_json()
        folder_path = data.get('folderPath')
        
        if not folder_path:
            return jsonify({"error": "Folder path is required"}), 400
        
        if not os.path.isdir(folder_path):
            return jsonify({"error": "Invalid folder path"}), 400
        
        # 生成任务ID
        task_id = f"reindex_task_{int(time.time())}"
        
        # 在新线程中重新处理文件夹
        thread = threading.Thread(target=process_folder_impl, args=(folder_path, task_id))
        thread.start()
        
        return jsonify({"taskId": task_id, "message": f"Started reindexing folder {folder_path}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500