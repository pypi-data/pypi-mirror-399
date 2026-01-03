import os
import sys
import argparse
import charset_normalizer
import pathspec

# 許可する拡張子（網羅的なリスト）
ALLOWED_EXTENSIONS = {
    # プログラミング言語
    '.py', '.pyw', '.pyi',  # Python
    '.js', '.mjs', '.cjs', '.jsx',  # JavaScript
    '.ts', '.tsx', '.d.ts',  # TypeScript
    '.java', '.kt', '.kts', '.scala',  # JVM系
    '.cs', '.vb', '.fs',  # .NET系
    '.cpp', '.cc', '.cxx', '.c', '.h', '.hpp', '.hxx',  # C/C++
    '.rs',  # Rust
    '.go', '.mod', '.sum',  # Go
    '.php', '.phtml',  # PHP
    '.rb', '.rbw', '.rake', '.gemspec',  # Ruby
    '.swift',  # Swift
    '.m', '.mm', '.h',  # Objective-C
    '.dart',  # Dart
    '.lua',  # Lua
    '.pl', '.pm', '.t',  # Perl
    '.r', '.R', '.rmd',  # R
    '.jl',  # Julia
    '.ex', '.exs',  # Elixir
    '.erl', '.hrl',  # Erlang
    '.clj', '.cljs', '.cljc',  # Clojure
    '.hs', '.lhs',  # Haskell
    '.ml', '.mli',  # OCaml
    '.elm',  # Elm
    '.nim',  # Nim
    '.zig',  # Zig
    '.v', '.vh', '.sv', '.svh',  # Verilog/SystemVerilog
    '.vhd', '.vhdl',  # VHDL
    
    # Web関連
    '.html', '.htm', '.xhtml',
    '.css', '.scss', '.sass', '.less', '.styl',
    '.vue', '.svelte',
    '.asp', '.aspx', '.jsp',
    
    # シェルスクリプト
    '.sh', '.bash', '.zsh', '.fish', '.ksh', '.csh',
    '.ps1', '.psm1', '.psd1',  # PowerShell
    '.bat', '.cmd',  # Windows Batch
    
    # データ・設定ファイル
    '.json', '.json5', '.jsonl',
    '.xml', '.xsd', '.xsl', '.xslt',
    '.yaml', '.yml',
    '.toml',
    '.ini', '.cfg', '.conf', '.config',
    '.env', '.envrc',
    '.properties',
    '.plist',
    '.reg',
    
    # ドキュメント・マークアップ
    '.md', '.markdown', '.mdown', '.mkd',
    '.rst', '.rest',
    '.txt', '.text',
    '.rtf',
    '.tex', '.latex', '.ltx',
    '.org',
    '.adoc', '.asciidoc',
    '.wiki',
    
    # データベース・クエリ
    '.sql', '.mysql', '.pgsql', '.plsql',
    '.cypher',
    '.graphql', '.gql',
    
    # ビルド・依存関係
    '.gradle', '.gradle.kts',
    '.maven', '.pom',
    '.cmake', '.cmakelist',
    '.make', '.mk', '.makefile',
    '.bazel', '.bzl',
    '.dockerfile', '.containerfile',
    '.vagrantfile',
    '.procfile',
    
    # パッケージ管理
    '.package.json', '.package-lock.json',
    '.yarn.lock', '.pnpm-lock.yaml',
    '.pipfile', '.pipfile.lock',
    '.requirements.txt', '.requirements-dev.txt',
    '.poetry.lock', '.pyproject.toml',
    '.gemfile', '.gemfile.lock',
    '.cargo.toml', '.cargo.lock',
    '.go.mod', '.go.sum',
    
    # CI/CD・設定
    '.gitignore', '.gitattributes', '.gitconfig',
    '.dockerignore',
    '.editorconfig',
    '.eslintrc', '.eslintignore',
    '.prettierrc', '.prettierignore',
    '.stylelintrc',
    '.babelrc',
    '.npmrc', '.yarnrc',
    
    # その他
    '.log', '.out', '.err',
    '.diff', '.patch',
    '.asm', '.s',  # Assembly
    '.f', '.f90', '.f95', '.f03', '.f08',  # Fortran
    '.cob', '.cbl',  # COBOL
    '.pas', '.pp',  # Pascal
    '.ada', '.adb', '.ads',  # Ada
    '.tcl', '.tk',  # Tcl/Tk
    '.vbs', '.vba',  # VBScript
    '.awk',  # AWK
    '.sed',  # sed
    '.flex', '.l',  # Flex
    '.y', '.yacc',  # Yacc/Bison
}

# 明示的に除外する拡張子
EXCLUDED_EXTENSIONS = {
    # 画像ファイル
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
    '.svg', '.ico', '.webp', '.avif', '.heic', '.raw',
    '.psd', '.ai', '.eps', '.indd',
    
    # 動画・音声ファイル
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv',
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
    
    # アーカイブ・圧縮ファイル
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
    '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2',
    '.cab', '.msi', '.deb', '.rpm',
    
    # バイナリ・実行ファイル
    '.exe', '.dll', '.so', '.dylib', '.a', '.lib',
    '.obj', '.o', '.pyc', '.pyo', '.pyd',
    '.class', '.jar', '.war', '.ear',
    '.wasm',
    
    # オフィス文書
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.odt', '.ods', '.odp', '.pages', '.numbers', '.key',
    '.pdf',
    
    # フォント
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    
    # データベースファイル
    '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb',
    
    # その他バイナリ
    '.bin', '.dat', '.dump', '.img', '.iso', '.dmg',
}

# 除外するディレクトリ
EXCLUDED_DIRECTORIES = {
    # Python
    '__pycache__', '.pytest_cache', '.mypy_cache', '.tox',
    'venv', '.venv', 'env', '.env',
    '.virtualenv', 'virtualenv',
    'site-packages', 'dist-packages',
    'build', 'dist',
    
    # Node.js
    'node_modules', '.npm', '.yarn', '.pnp',
    
    # Version Control
    '.git', '.svn', '.hg', '.bzr',
    
    # IDEs
    '.vscode', '.idea', '.vs', '.eclipse',
    '.sublime-project', '.sublime-workspace',
    
    # Rust
    'target',
    
    # Go
    'vendor',
    
    # Java
    '.gradle', '.m2', 'out',
    
    # .NET
    'bin', 'obj', 'packages',
    
    # Ruby
    '.bundle',
    
    # PHP
    '.composer',
    
    # Temporary/Cache
    'tmp', 'temp', '.tmp', '.temp',
    'cache', '.cache', 'caches',
    'logs', '.logs',
    
    # Coverage/Testing
    'coverage', '.coverage', '.nyc_output',
    'htmlcov', 'cov_html',
    
    # Documentation builds
    '_build', 'site',
}

# テキストファイルとして確実に扱う拡張子（バイナリ判定をスキップ）
KNOWN_TEXT_EXTENSIONS = {
    '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
    '.vue', '.svelte', '.astro',
    '.json', '.json5', '.jsonc',
    '.css', '.scss', '.sass', '.less',
    '.html', '.htm', '.xml', '.svg',
    '.md', '.markdown', '.txt', '.text',
    '.py', '.pyw', '.pyi',
    '.yaml', '.yml', '.toml', '.ini',
    '.sh', '.bash', '.ps1', '.bat',
    '.sql', '.graphql', '.gql',
}

# バイナリファイルのマジックナンバー
BINARY_SIGNATURES = [
    b'\x7fELF',      # ELF
    b'MZ',           # PE
    b'\xfe\xed\xfa', # Mach-O
    b'\x89PNG',      # PNG
    b'\xff\xd8\xff', # JPEG
    b'GIF8',         # GIF
    b'BM',           # BMP
    b'\x50\x4b',     # ZIP/JAR/DOCX
]


def load_gitignore_patterns(directory):
    """
    指定ディレクトリから .gitignore を読み込み、pathspec.PathSpec を返す
    
    Args:
        directory (str): 検索するルートディレクトリ
    
    Returns:
        pathspec.PathSpec or None: パターンマッチャー、.gitignoreがない場合はNone
    """
    gitignore_path = os.path.join(directory, '.gitignore')
    
    if not os.path.exists(gitignore_path):
        return None
    
    try:
        with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # 空行とコメント行を除外
        patterns = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                patterns.append(line)
        
        if not patterns:
            return None
        
        # pathspec.PathSpecを生成
        spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
        return spec
        
    except Exception as e:
        print(f"Warning: Could not read .gitignore: {e}", file=sys.stderr)
        return None


def is_ignored_by_gitignore(file_path, root_directory, spec):
    """
    pathspecを使用してファイルが .gitignore で除外されるか判定
    
    Args:
        file_path (str): チェックするファイルの絶対パス
        root_directory (str): .gitignore が存在するルートディレクトリ
        spec (pathspec.PathSpec): パターンマッチャー
    
    Returns:
        bool: 除外される場合 True
    """
    try:
        # 相対パスを計算
        relative_path = os.path.relpath(file_path, root_directory)
        # パス区切り文字を / に統一
        relative_path = relative_path.replace('\\', '/')
        
        # ファイルがマッチするかチェック
        if spec.match_file(relative_path):
            return True
        
        # ディレクトリの場合、末尾に / を追加して再チェック
        if os.path.isdir(file_path):
            if spec.match_file(relative_path + '/'):
                return True
        
        return False
        
    except Exception:
        return False


def is_binary_file(file_path, chunk_size=8192):
    """
    ファイル先頭をチェックしてバイナリファイルを判定（改善版）
    
    Args:
        file_path (str): チェックするファイルのパス
        chunk_size (int): 読み込むバイト数
    
    Returns:
        bool: バイナリファイルの場合 True
    """
    # 拡張子ベースの早期リターン
    _, ext = os.path.splitext(file_path.lower())
    if ext in KNOWN_TEXT_EXTENSIONS:
        return False
    
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            if not chunk:
                return False
            
            # マジックナンバーチェック
            for signature in BINARY_SIGNATURES:
                if chunk.startswith(signature):
                    return True
            
            # NULL文字があればバイナリ
            if b'\x00' in chunk:
                return True
            
            # 制御文字の割合をチェック（より寛容に）
            control_chars = sum(1 for b in chunk if b < 32 and b not in [9, 10, 11, 12, 13])
            # 絶対数と割合の両方でチェック
            if control_chars > 100 and len(chunk) > 0 and control_chars / len(chunk) > 0.1:
                return True
            # 割合のみのチェックはより寛容に
            if len(chunk) > 0 and control_chars / len(chunk) > 0.3:
                return True
                
    except Exception:
        return True
    
    return False


def should_exclude_directory(dir_path):
    """ディレクトリパスが除外対象かチェック"""
    path_parts = dir_path.replace('\\', '/').split('/')
    
    for part in path_parts:
        if part in EXCLUDED_DIRECTORIES:
            return True
        # .egg-info のようなパターンマッチング
        if part.endswith('.egg-info'):
            return True
    
    return False


def should_include_file(file_path, gitignore_spec=None, root_directory=None, stats=None, verbose=False):
    """
    ファイルパス全体を考慮して含めるべきかチェック（v0.3.0改善版）
    
    Args:
        file_path (str): チェックするファイルの絶対パス
        gitignore_spec (pathspec.PathSpec): .gitignoreのパターンマッチャー
        root_directory (str): ルートディレクトリ
        stats (dict): 統計情報を記録する辞書
        verbose (bool): 詳細ログ出力
    
    Returns:
        bool: ファイルを含める場合 True
    """
    if stats is not None:
        stats['total_scanned'] += 1
    
    # 相対パス（ログ用）
    rel_path = os.path.relpath(file_path, root_directory) if root_directory else file_path
    
    # 1. .gitignore チェック（最優先）
    if gitignore_spec is not None and root_directory is not None:
        if is_ignored_by_gitignore(file_path, root_directory, gitignore_spec):
            if verbose:
                print(f"  ✗ {rel_path} (excluded: .gitignore rule)")
            if stats is not None:
                stats['excluded_by_gitignore'] += 1
            return False
    
    # 2. ディレクトリチェック
    dir_path = os.path.dirname(file_path)
    if should_exclude_directory(dir_path):
        if verbose:
            print(f"  ✗ {rel_path} (excluded: directory)")
        if stats is not None:
            stats['excluded_by_directory'] += 1
        return False
    
    file_name = os.path.basename(file_path)
    _, ext = os.path.splitext(file_name.lower())
    
    # 3. 隠しファイルの除外（一部設定ファイルは許可）
    if file_name.startswith('.') and file_name.lower() not in {
        '.gitignore', '.gitattributes', '.editorconfig', '.eslintrc', 
        '.prettierrc', '.stylelintrc', '.babelrc', '.npmrc', '.yarnrc'
    }:
        if verbose:
            print(f"  ✗ {rel_path} (excluded: hidden file)")
        if stats is not None:
            stats['excluded_by_extension'] += 1
        return False
    
    # 4. 明示的に除外する拡張子
    if ext in EXCLUDED_EXTENSIONS:
        if verbose:
            print(f"  ✗ {rel_path} (excluded: file type '{ext}')")
        if stats is not None:
            stats['excluded_by_extension'] += 1
        return False
    
    # 5. 許可される拡張子
    if ext in ALLOWED_EXTENSIONS:
        if verbose:
            print(f"  ✓ {rel_path} (included)")
        if stats is not None:
            stats['included'] += 1
        return True
    
    # 6. 拡張子なしのファイル（シェルスクリプトなど）
    if not ext:
        # よくある設定ファイル名
        config_files = {
            'dockerfile', 'containerfile', 'makefile', 'rakefile', 
            'gemfile', 'procfile', 'vagrantfile', 'jenkinsfile',
            'readme', 'license', 'changelog', 'contributing',
            'authors', 'contributors', 'maintainers'
        }
        if file_name.lower() in config_files:
            if verbose:
                print(f"  ✓ {rel_path} (included)")
            if stats is not None:
                stats['included'] += 1
            return True
        
        # バイナリファイルでなければ含める
        if not is_binary_file(file_path):
            if verbose:
                print(f"  ✓ {rel_path} (included)")
            if stats is not None:
                stats['included'] += 1
            return True
        else:
            if verbose:
                print(f"  ✗ {rel_path} (excluded: binary detection)")
            if stats is not None:
                stats['excluded_by_binary'] += 1
            return False
    
    # 7. その他の拡張子: バイナリチェック
    if not is_binary_file(file_path):
        if verbose:
            print(f"  ✓ {rel_path} (included)")
        if stats is not None:
            stats['included'] += 1
        return True
    
    if verbose:
        print(f"  ✗ {rel_path} (excluded: binary detection)")
    if stats is not None:
        stats['excluded_by_binary'] += 1
    return False


def get_file_list(directory, max_files=None, gitignore_spec=None, stats=None, verbose=False):
    """
    ファイルリストを取得（v0.3.0改善版）
    
    Args:
        directory (str): スキャンするディレクトリ
        max_files (int): 早期終了するファイル数制限
        gitignore_spec (pathspec.PathSpec): .gitignoreのパターンマッチャー
        stats (dict): 統計情報を記録する辞書
        verbose (bool): 詳細ログ出力
    
    Returns:
        tuple: (file_list, has_more) - ファイルリストと制限到達フラグ
    """
    file_list = []
    file_count = 0
    
    for root, dirs, files in os.walk(directory):
        # .gitignoreによるディレクトリ除外
        if gitignore_spec:
            dirs[:] = [d for d in dirs 
                      if not is_ignored_by_gitignore(os.path.join(root, d), directory, gitignore_spec)]
        
        # 既存のディレクトリ除外
        dirs[:] = [d for d in dirs if not should_exclude_directory(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            if should_include_file(file_path, gitignore_spec, directory, stats, verbose):
                file_list.append(file_path)
                file_count += 1
                
                # 早期チェック機能
                if max_files and file_count >= max_files:
                    return file_list, True  # 制限に達したことを示すフラグ
    
    return file_list, False


def build_tree_structure(file_list, root_directory):
    """
    ファイルリストから木構造の辞書を構築
    
    Args:
        file_list (list): 絶対パスのリスト
        root_directory (str): ルートディレクトリ
    
    Returns:
        dict: 木構造の辞書
    """
    tree = {}
    
    for file_path in file_list:
        # 相対パスを取得
        try:
            rel_path = os.path.relpath(file_path, root_directory)
        except ValueError:
            # Windowsで異なるドライブの場合など
            continue
        
        # パスを / で分割
        parts = rel_path.replace('\\', '/').split('/')
        
        # 木構造に追加
        current = tree
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # ファイル
                if '__files__' not in current:
                    current['__files__'] = []
                current['__files__'].append(part)
            else:
                # ディレクトリ
                if part not in current:
                    current[part] = {}
                current = current[part]
    
    return tree


def format_tree_structure(tree, prefix='', is_last=True, root_name=None):
    """
    木構造の辞書を視覚的なツリー文字列に変換（再帰関数）
    
    Args:
        tree (dict): build_tree_structure() で構築した木構造
        prefix (str): 現在の行のプレフィックス（インデント）
        is_last (bool): 現在の要素が兄弟の中で最後か
        root_name (str): ルートディレクトリ名（最初の呼び出し時のみ）
    
    Returns:
        str: フォーマットされたツリー文字列
    """
    lines = []
    
    # ルートレベルの場合
    if root_name is not None:
        lines.append(f"└── {root_name}/")
        prefix = '    '
    
    # ディレクトリキーを取得（__files__を除く）
    dir_keys = sorted([k for k in tree.keys() if k != '__files__'])
    # ファイルを取得
    files = sorted(tree.get('__files__', []))
    
    # 全要素（ディレクトリ + ファイル）
    all_items = dir_keys + files
    total_items = len(all_items)
    
    for idx, item in enumerate(all_items):
        is_last_item = (idx == total_items - 1)
        
        if item in dir_keys:
            # ディレクトリ
            connector = '└── ' if is_last_item else '├── '
            lines.append(f"{prefix}{connector}{item}/")
            
            # 新しいプレフィックス
            new_prefix = prefix + ('    ' if is_last_item else '│   ')
            
            # 再帰呼び出し
            subtree_lines = format_tree_structure(
                tree[item], 
                prefix=new_prefix, 
                is_last=is_last_item
            )
            lines.append(subtree_lines)
        else:
            # ファイル
            connector = '└── ' if is_last_item else '├── '
            lines.append(f"{prefix}{connector}{item}")
    
    return '\n'.join(lines)


def generate_tree_output(file_list, root_directory):
    """
    ファイルリストからツリー出力文字列を生成（統合関数）
    
    Args:
        file_list (list): 絶対パスのリスト
        root_directory (str): ルートディレクトリ
    
    Returns:
        str: フォーマットされたツリー文字列
    """
    if not file_list:
        return ""
    
    tree = build_tree_structure(file_list, root_directory)
    root_name = os.path.basename(root_directory) or 'root'
    return format_tree_structure(tree, root_name=root_name)


def detect_encoding(file_path):
    """charset-normalizerを使用した高精度エンコーディング検出"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            
        result = charset_normalizer.from_bytes(raw_data)
        if result.best():
            return result.best().encoding
        else:
            return 'utf-8'
    except Exception:
        return 'utf-8'


def read_file_content(file_path, stats=None, verbose=False):
    """
    ファイル内容を読み込み、エラーを適切に処理
    
    Args:
        file_path (str): 読み込むファイルのパス
        stats (dict): 統計情報の辞書
        verbose (bool): 詳細ログ出力
    
    Returns:
        str or None: ファイル内容、読み込み失敗時はNone
    """
    try:
        # エンコーディング検出
        encoding = detect_encoding(file_path)
        
        if verbose:
            rel_path = os.path.basename(file_path)
            print(f"  Reading {rel_path} (encoding: {encoding})")
        
        # 読み込み試行
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # フォールバック1: UTF-8 with errors='replace'
            if verbose:
                print(f"  Warning: Decoding error, retrying with UTF-8 (replace mode)")
            if stats is not None:
                stats['decode_errors'] += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
            except Exception:
                # フォールバック2: Latin-1（常に成功する）
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
                    
    except (IOError, OSError) as e:
        print(f"Error: Could not read {file_path}: {e}", file=sys.stderr)
        if stats is not None:
            stats['read_errors'] += 1
        return None
    except Exception as e:
        print(f"Error: Unexpected error reading {file_path}: {e}", file=sys.stderr)
        if stats is not None:
            stats['read_errors'] += 1
        return None


def create_prompt_file(directory, file_list, stats=None, verbose=False):
    """
    プロンプトファイルを作成（v0.3.0: ツリー構造を含む）
    
    Args:
        directory (str): 出力先ディレクトリ
        file_list (list): ファイルパスのリスト
        stats (dict): 統計情報の辞書
        verbose (bool): 詳細ログ出力
    """
    prompt_file = os.path.join(directory, 'prompt.txt')
    
    try:
        with open(prompt_file, 'w', encoding='utf-8') as outfile:
            # ツリー構造を出力
            outfile.write("Directory Structure:\n")
            outfile.write("=" * 80 + "\n\n")
            tree_output = generate_tree_output(file_list, directory)
            outfile.write(tree_output)
            outfile.write("\n\n")
            
            # ファイル内容を出力
            outfile.write("Files Content:\n")
            outfile.write("=" * 80 + "\n\n")
            
            for file_path in file_list:
                rel_path = os.path.relpath(file_path, directory)
                outfile.write(f"{rel_path}:\n")
                
                content = read_file_content(file_path, stats, verbose)
                if content is not None:
                    outfile.write(content)
                    outfile.write("\n\n")
                else:
                    outfile.write("[Error: Could not read file]\n\n")
                    
    except IOError as e:
        print(f"Error creating prompt file: {e}", file=sys.stderr)
        sys.exit(1)


def create_split_prompt_files(directory, file_list, split_count, stats=None, verbose=False):
    """
    分割プロンプトファイルを作成（v0.3.0: 各ファイルにツリー構造を含む）
    
    Args:
        directory (str): 出力先ディレクトリ
        file_list (list): ファイルパスのリスト
        split_count (int): 分割数
        stats (dict): 統計情報の辞書
        verbose (bool): 詳細ログ出力
    """
    files_per_split = len(file_list) // split_count
    remainder = len(file_list) % split_count
    
    # ツリー構造は一度だけ生成（全ファイル分）
    tree_output = generate_tree_output(file_list, directory)
    
    start_idx = 0
    for i in range(split_count):
        # 各分割のファイル数を計算
        chunk_size = files_per_split + (1 if i < remainder else 0)
        end_idx = start_idx + chunk_size
        
        # 分割されたファイルリストを取得
        chunk_files = file_list[start_idx:end_idx]
        prompt_file = os.path.join(directory, f'prompt_{i+1}.txt')
        
        # 各プロンプトファイルを作成
        try:
            with open(prompt_file, 'w', encoding='utf-8') as outfile:
                # ツリー構造を出力（全ファイル分）
                outfile.write(f"Directory Structure (Part {i+1}/{split_count}):\n")
                outfile.write("=" * 80 + "\n\n")
                outfile.write(tree_output)
                outfile.write("\n\n")
                
                # ファイル内容を出力（この分割に含まれるファイルのみ）
                outfile.write(f"Files Content (Part {i+1}/{split_count}):\n")
                outfile.write("=" * 80 + "\n\n")
                
                for file_path in chunk_files:
                    rel_path = os.path.relpath(file_path, directory)
                    outfile.write(f"{rel_path}:\n")
                    
                    content = read_file_content(file_path, stats, verbose)
                    if content is not None:
                        outfile.write(content)
                        outfile.write("\n\n")
                    else:
                        outfile.write("[Error: Could not read file]\n\n")
                        
        except IOError as e:
            print(f"Error creating prompt file: {e}", file=sys.stderr)
            sys.exit(1)
            
        start_idx = end_idx


def get_user_confirmation(message):
    """ユーザー確認を取得"""
    while True:
        response = input(message).lower()
        if response in ['y', 'n']:
            return response == 'y'
        print("Invalid input. Please enter 'y' or 'n'.")


def print_statistics(stats, verbose=False):
    """
    処理統計を見やすく出力
    
    Args:
        stats (dict): 統計情報
        verbose (bool): 詳細モード
    """
    print("\nStatistics:")
    print("─" * 40)
    print(f"Total files scanned: {stats['total_scanned']:,}")
    print(f"Files included:      {stats['included']:,}")
    
    excluded_total = (stats['excluded_by_gitignore'] + 
                     stats['excluded_by_directory'] + 
                     stats['excluded_by_extension'] + 
                     stats['excluded_by_binary'])
    print(f"Files excluded:      {excluded_total:,}")
    
    if verbose:
        print(f"  ├─ By .gitignore:        {stats['excluded_by_gitignore']:,}")
        print(f"  ├─ By directory:         {stats['excluded_by_directory']:,}")
        print(f"  ├─ By extension:         {stats['excluded_by_extension']:,}")
        print(f"  └─ By binary detection:  {stats['excluded_by_binary']:,}")
    
    # 警告がある場合のみ表示
    if stats['decode_errors'] > 0 or stats['read_errors'] > 0:
        print("\nWarnings:")
        if stats['decode_errors'] > 0:
            print(f"  ├─ Decoding errors: {stats['decode_errors']}")
        if stats['read_errors'] > 0:
            print(f"  └─ Read errors:     {stats['read_errors']}")


def main():
    """メイン関数（v0.3.0）"""
    # 引数解析
    parser = argparse.ArgumentParser(
        description='Convert source files to prompt files',
        epilog='Example: s2p . --verbose'
    )
    parser.add_argument('directory', 
                       help='Target directory or "here" for current directory')
    parser.add_argument('--cut', type=int, 
                       help='Split output into specified number of files')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed processing information')
    parser.add_argument('--debug', action='store_true',
                       help='Show debug information for troubleshooting')
    
    args = parser.parse_args()
    
    # ディレクトリ解決
    if args.directory == 'here':
        directory = os.getcwd()
    else:
        directory = os.path.abspath(args.directory)
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.", file=sys.stderr)
        sys.exit(1)
    
    # 統計情報の初期化
    statistics = {
        'total_scanned': 0,
        'included': 0,
        'excluded_by_gitignore': 0,
        'excluded_by_directory': 0,
        'excluded_by_extension': 0,
        'excluded_by_binary': 0,
        'decode_errors': 0,
        'read_errors': 0
    }
    
    # .gitignore の読み込み
    gitignore_spec = load_gitignore_patterns(directory)
    if gitignore_spec and (args.verbose or args.debug):
        print("Found .gitignore: Applying exclusion rules")
    
    # 早期ファイルスキャン（50件まで）
    if args.verbose or args.debug:
        print(f"\nScanning directory: {directory}")
        print("Processing files...\n")
    
    file_list, has_more = get_file_list(
        directory, 
        max_files=50, 
        gitignore_spec=gitignore_spec,
        stats=statistics,
        verbose=args.verbose
    )
    
    if not file_list:
        print(f"No text files found in {directory}")
        sys.exit(1)
    
    # 50ファイル以上の確認
    if has_more:
        message = "More than 50 files found. Continue processing all files? (y/n): "
        if get_user_confirmation(message):
            # 統計をリセット
            for key in statistics:
                statistics[key] = 0
            
            file_list, _ = get_file_list(
                directory,
                gitignore_spec=gitignore_spec,
                stats=statistics,
                verbose=args.verbose
            )
        else:
            print("Operation cancelled.")
            sys.exit(0)
    
    # プロンプトファイル生成
    if args.cut and args.cut > 0:
        create_split_prompt_files(
            os.path.abspath(directory), 
            file_list, 
            args.cut,
            stats=statistics,
            verbose=args.verbose
        )
        print(f"\nCreated {args.cut} prompt files in: {os.path.abspath(directory)}")
    else:
        create_prompt_file(
            os.path.abspath(directory), 
            file_list,
            stats=statistics,
            verbose=args.verbose
        )
        print(f"\nPrompt file created: {os.path.join(os.path.abspath(directory), 'prompt.txt')}")
    
    # 統計出力
    if args.verbose or args.debug:
        print_statistics(statistics, verbose=args.verbose)


if __name__ == '__main__':
    main()
