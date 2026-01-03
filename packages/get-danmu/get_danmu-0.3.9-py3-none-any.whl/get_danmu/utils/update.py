import sqlite3
import os


def check_and_add_updatetime_field(db_file='danmu_data.db', table_name='anime_episodes'):
    """
    检查并添加updateTime字段到指定表
    
    Args:
        db_file (str): 数据库文件路径
        table_name (str): 表名
    """
    try:
        # 检查数据库文件是否存在
        if not os.path.exists(db_file):
            print(f"❌ 数据库文件 '{db_file}' 不存在")
            return False
        
        # 连接到数据库
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print(f"✅ 成功连接到数据库: {db_file}")
        
        # 检查表是否存在
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print(f"❌ 表 '{table_name}' 不存在于数据库中")
            conn.close()
            return False
        
        print(f"✅ 表 '{table_name}' 存在")
        
        # 获取表的所有字段
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\n📋 表 '{table_name}' 的当前字段:")
        column_names = []
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            col_notnull = col[3]
            col_default = col[4]
            col_pk = col[5]
            
            column_names.append(col_name.lower())
            
            # 格式化输出
            constraints = []
            if col_pk:
                constraints.append("PRIMARY KEY")
            if col_notnull:
                constraints.append("NOT NULL")
            if col_default is not None:
                constraints.append(f"DEFAULT {col_default}")
            
            constraint_str = " " + ", ".join(constraints) if constraints else ""
            print(f"   - {col_name}: {col_type}{constraint_str}")
        
        # 检查是否存在updateTime字段（不区分大小写）
        has_updatetime = 'updatetime' in column_names
        
        if has_updatetime:
            print(f"\n✅ 表 '{table_name}' 已包含 'updateTime' 字段")
            conn.close()
            return True
        else:
            print(f"\nℹ️  表 '{table_name}' 缺少 'updateTime' 字段，正在添加...")
            
            # 添加updateTime字段（可以为空的datetime类型）
            try:
                cursor.execute(f"""
                ALTER TABLE {table_name} 
                ADD COLUMN updateTime DATETIME
                """)
                
                conn.commit()
                print(f"✅ 成功添加 'updateTime DATETIME' 字段到表 '{table_name}'")
                
                # 验证添加结果
                cursor.execute(f"PRAGMA table_info({table_name})")
                new_columns = cursor.fetchall()
                new_column_names = [col[1].lower() for col in new_columns]
                
                if 'updatetime' in new_column_names:
                    print(f"✅ 验证成功：'updateTime' 字段已添加到表中")
                else:
                    print(f"❌ 验证失败：'updateTime' 字段未添加成功")
                
                conn.close()
                return True
                
            except sqlite3.Error as e:
                print(f"❌ 添加字段时出错: {e}")
                conn.rollback()
                conn.close()
                return False
    
    except sqlite3.Error as e:
        print(f"❌ 数据库操作错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False