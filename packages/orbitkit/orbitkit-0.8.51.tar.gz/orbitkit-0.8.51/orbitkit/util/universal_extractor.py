import os
import shutil
import tempfile
import zipfile
import tarfile
from pathlib import Path
from typing import Optional, List, Union, Set
import logging
import platform

try:
    import rarfile
    import py7zr
except ImportError:
    raise ValueError(
        "Please install below packages before using this function.\n"
        "- rarfile\n"
        "- py7zr\n"
    )

logger = logging.getLogger(__name__)

if platform.system() == 'Windows':
    logger.warning(
        "Windows system requires additional UnRAR tool to extract RAR files. Please download and install UnRAR from https://www.rarlab.com/rar_add.htm")


class UniversalExtractor:
    """
    通用压缩文件解压类，支持常见压缩格式和特殊情况处理

    可以作为上下文管理器使用以自动清理临时目录：
    with UniversalExtractor() as extractor:
        result = extractor.extract('file.zip')
    """

    # 支持的压缩格式及其对应扩展名
    SUPPORTED_FORMATS = {
        'zip': ['.zip'],
        'tar': ['.tar'],
        'tar.gz': ['.tar.gz', '.tgz'],
        'tar.bz2': ['.tar.bz2', '.tbz2'],
        'tar.xz': ['.tar.xz', '.txz'],
        'rar': ['.rar'],
        '7z': ['.7z']
    }

    def __init__(self):
        self.temp_dir = None
        self._temp_dirs = []  # 跟踪所有创建的临时目录

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出，清理临时目录"""
        self.cleanup()
        return False

    def cleanup(self):
        """清理所有临时目录"""
        for temp_dir in self._temp_dirs:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    logger.info(f"已清理临时目录: {temp_dir}")
                except Exception as e:
                    logger.warning(f"清理临时目录失败 {temp_dir}: {str(e)}")
        self._temp_dirs.clear()
        self.temp_dir = None

    def _get_file_format(self, file_path: Union[str, Path]) -> Optional[str]:
        """根据文件扩展名判断压缩格式"""
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        # 检查多部分扩展名（如.tar.gz）
        if len(file_path.suffixes) > 1:
            multi_suffix = ''.join(file_path.suffixes[-2:]).lower()
            for format_name, extensions in self.SUPPORTED_FORMATS.items():
                if multi_suffix in extensions:
                    return format_name

        # 检查单扩展名
        for format_name, extensions in self.SUPPORTED_FORMATS.items():
            if suffix in extensions:
                return format_name

        return None

    def _create_output_dir(self, output_path: Optional[str] = None) -> str:
        """创建输出目录"""
        if output_path:
            os.makedirs(output_path, exist_ok=True)
            return output_path
        else:
            self.temp_dir = tempfile.mkdtemp(prefix="unpack_")
            self._temp_dirs.append(self.temp_dir)  # 跟踪临时目录
            return self.temp_dir

    def _extract_zip(self, archive_path: str, output_path: str, password: Optional[str] = None) -> List[str]:
        """解压ZIP文件"""
        extracted_files = []

        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                # 尝试检测加密文件
                encrypted_files = [f for f in zip_ref.namelist() if zip_ref.getinfo(f).flag_bits & 0x1]
                if encrypted_files and not password:
                    logger.warning("发现加密文件，但未提供密码")

                # 尝试解压
                try:
                    zip_ref.extractall(output_path, pwd=password.encode() if password else None)
                except RuntimeError as e:
                    if "Bad password" in str(e) or "password" in str(e).lower():
                        raise ValueError("密码错误或需要密码") from e
                    raise

                # 获取所有提取的文件
                for member in zip_ref.namelist():
                    member_path = os.path.join(output_path, member)
                    if os.path.exists(member_path) and os.path.isfile(member_path):
                        extracted_files.append(member_path)

        except zipfile.BadZipFile:
            raise ValueError("ZIP文件损坏或格式不正确")

        return extracted_files

    def _extract_tar(self, archive_path: str, output_path: str) -> List[str]:
        """解压TAR文件"""
        extracted_files = []

        try:
            with tarfile.open(archive_path, 'r') as tar_ref:
                # 安全提取，防止路径遍历攻击
                safe_members = []
                for member in tar_ref.getmembers():
                    # 确保成员路径安全
                    member_path = os.path.normpath(member.name)
                    if member_path.startswith(('..', '/', '\\')):
                        # 只保留文件名，移除危险路径
                        member.name = os.path.basename(member_path)
                        logger.warning(f"检测到不安全路径，已重命名: {member_path} -> {member.name}")
                    safe_members.append(member)

                # 只提取安全的成员
                for member in safe_members:
                    tar_ref.extract(member, output_path)
                    if member.isfile():
                        member_path = os.path.join(output_path, member.name)
                        if os.path.exists(member_path):
                            extracted_files.append(member_path)

        except tarfile.ReadError:
            raise ValueError("TAR文件损坏或格式不正确")

        return extracted_files

    def _extract_rar(self, archive_path: str, output_path: str, password: Optional[str] = None) -> List[str]:
        """解压RAR文件"""
        extracted_files = []

        try:
            # 检查是否安装了unrar工具
            if not rarfile.UNRAR_TOOL:
                logger.warning("未找到unrar工具，RAR解压可能受限")

            with rarfile.RarFile(archive_path, 'r') as rar_ref:
                # 尝试解压
                try:
                    rar_ref.extractall(output_path, pwd=password)
                except rarfile.PasswordRequired:
                    raise ValueError("需要密码来解压RAR文件")
                except rarfile.RarCannotExec:
                    raise ValueError("需要unrar工具，无法解压RAR文件")

                # 获取所有提取的文件
                for member in rar_ref.infolist():
                    if not member.isdir():
                        member_path = os.path.join(output_path, member.filename)
                        if os.path.exists(member_path):
                            extracted_files.append(member_path)

        except rarfile.NotRarFile:
            raise ValueError("不是有效的RAR文件")
        except rarfile.BadRarFile:
            raise ValueError("RAR文件损坏或格式不正确")
        except rarfile.NeedFirstVolume:
            raise ValueError("需要多卷RAR文件的第一卷")

        return extracted_files

    def _extract_7z(self, archive_path: str, output_path: str, password: Optional[str] = None) -> List[str]:
        """解压7Z文件"""
        extracted_files = []

        try:
            with py7zr.SevenZipFile(archive_path, 'r', password=password) as zip_ref:
                zip_ref.extractall(output_path)

                # 获取所有提取的文件
                for member in zip_ref.list():
                    if not member.is_directory:
                        member_path = os.path.join(output_path, member.filename)
                        if os.path.exists(member_path):
                            extracted_files.append(member_path)

        except py7zr.Bad7zFile:
            raise ValueError("7Z文件损坏或格式不正确")
        except py7zr.PasswordRequired:
            raise ValueError("需要密码来解压7Z文件")
        except Exception as e:
            if str(e) == 'Corrupt input data':
                raise ValueError("7Z文件密码错误")
            raise e

        return extracted_files

    def _remove_empty_directories(self, directory: str):
        """递归删除空目录"""
        for root, dirs, files in os.walk(directory, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    # 尝试删除目录，如果目录不为空会抛出OSError异常
                    os.rmdir(dir_path)
                    logger.debug(f"删除空目录: {dir_path}")
                except OSError:
                    # 目录非空，保留
                    pass

    def _flatten_directory(self, directory: str):
        """将目录中的所有文件移动到顶层目录，并删除子目录"""
        # 先收集所有需要移动的文件，避免在遍历时修改目录结构
        files_to_move = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                src_path = os.path.join(root, file)
                # 如果文件不在顶层目录
                if root != directory:
                    files_to_move.append((src_path, file))

        # 然后再移动文件
        for src_path, file in files_to_move:
            # 生成目标文件名，处理同名文件
            base_name = file
            dest_path = os.path.join(directory, base_name)
            counter = 1

            # 处理文件名冲突
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(base_name)
                dest_path = os.path.join(directory, f"{name}_{counter}{ext}")
                counter += 1

            # 移动文件
            try:
                shutil.move(src_path, dest_path)
            except FileNotFoundError:
                # 文件可能已被移动，跳过
                logger.warning(f"文件不存在，跳过: {src_path}")

        # 删除所有子目录
        self._remove_empty_directories(directory)

    def _handle_nested_archives(self, output_path: str, password: Optional[str] = None,
                                recursive: bool = True, current_depth: int = 0):
        """处理嵌套压缩文件（压缩包中的压缩包）"""
        if not recursive:
            return

        max_nested_level = 10  # 防止无限递归
        if current_depth >= max_nested_level:
            logger.warning(f"达到最大嵌套深度 {max_nested_level}，停止递归解压")
            return

        # 先收集所有压缩文件，避免在遍历时修改目录结构
        archive_files = []
        for root, _, files in os.walk(output_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_format = self._get_file_format(file_path)
                if file_format:
                    archive_files.append(file_path)

        # 然后处理所有收集到的压缩文件
        for file_path in archive_files:
            if not os.path.exists(file_path):
                # 文件可能已被删除
                continue

            try:
                # 为嵌套压缩包创建解压目录，处理多扩展名
                file_format = self._get_file_format(file_path)
                # 获取不含压缩扩展名的路径
                nested_output = self._get_path_without_archive_extension(file_path, file_format)
                os.makedirs(nested_output, exist_ok=True)

                # 递归解压，增加深度
                self._extract_file_internal(file_path, nested_output, password, recursive, current_depth + 1)

                # 删除原始压缩包
                os.remove(file_path)
                logger.info(f"已解压嵌套压缩文件 (深度 {current_depth + 1}): {file_path}")

            except Exception as e:
                logger.warning(f"无法解压嵌套压缩文件 {file_path}: {str(e)}")
                # 保留原始压缩包

    def is_archive_file(self, file_path: Union[str, Path]) -> bool:
        """根据文件扩展名判断是否为压缩文件"""
        file_format = self._get_file_format(file_path)
        return False if not file_format else True

    def _get_path_without_archive_extension(self, file_path: str, file_format: str) -> str:
        """获取去除压缩扩展名后的路径，处理多扩展名如 .tar.gz"""
        path = Path(file_path)

        # 对于多部分扩展名
        if file_format in ['tar.gz', 'tar.bz2', 'tar.xz']:
            # 移除两个扩展名
            return str(path.parent / path.stem.rsplit('.', 1)[0])
        else:
            # 单扩展名
            return str(path.parent / path.stem)

    def _extract_file_internal(self,
                               archive_path: Union[str, Path],
                               output_path: str,
                               password: Optional[str] = None,
                               recursive: bool = True,
                               current_depth: int = 0) -> List[str]:
        """
        内部解压方法，支持深度追踪
        """
        # 获取文件格式
        file_format = self._get_file_format(archive_path)
        if not file_format:
            raise ValueError(f"不支持的压缩格式: {archive_path}")

        # 根据格式选择解压方法
        if file_format == 'zip':
            extracted_files = self._extract_zip(str(archive_path), output_path, password)
        elif file_format in ['tar', 'tar.gz', 'tar.bz2', 'tar.xz']:
            extracted_files = self._extract_tar(str(archive_path), output_path)
        elif file_format == 'rar':
            extracted_files = self._extract_rar(str(archive_path), output_path, password)
        elif file_format == '7z':
            extracted_files = self._extract_7z(str(archive_path), output_path, password)
        else:
            raise ValueError(f"不支持的压缩格式: {file_format}")

        logger.info(f"成功解压 {len(extracted_files)} 个文件")

        # 处理嵌套压缩文件
        if recursive:
            self._handle_nested_archives(output_path, password, recursive, current_depth)

        return extracted_files

    def _extract_file(self,
                      archive_path: Union[str, Path],
                      output_path: str,
                      password: Optional[str] = None,
                      recursive: bool = True) -> List[str]:
        """
        解压方法的公共接口
        """
        return self._extract_file_internal(archive_path, output_path, password, recursive, current_depth=0)

    def _filter_files_by_extension(self, directory: str, extensions: Optional[Set[str]] = None) -> List[str]:
        """根据扩展名过滤文件，删除不符合条件的文件并清理空文件夹"""
        if not extensions:
            return []

        kept_files = []
        removed_files = []

        # 首先收集所有文件并分类
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()

                if file_ext in extensions:
                    kept_files.append(file_path)
                else:
                    removed_files.append(file_path)

        # 然后删除不需要的文件
        for file_path in removed_files:
            try:
                os.remove(file_path)
            except FileNotFoundError:
                logger.warning(f"文件已不存在，跳过删除: {file_path}")

        logger.info(f"根据扩展名过滤: 保留了 {len(kept_files)} 个文件, 删除了 {len(removed_files)} 个文件")

        # 清理空目录
        self._remove_empty_directories(directory)

        return kept_files

    def extract(self,
                archive_path: Union[str, Path],
                output_path: Optional[str] = None,
                password: Optional[str] = None,
                flatten: bool = False,
                recursive: bool = True,
                extensions: Optional[List[str]] = None) -> str:
        """
        解压压缩文件

        参数:
            archive_path: 压缩文件路径
            output_path: 输出目录路径，如果为None则使用临时目录
            password: 解压密码（如果需要）
            flatten: 是否将所有文件提取到同一级目录，默认为 False
            recursive: 是否递归解压嵌套压缩文件，默认为 True
            extensions: 只保留指定扩展名的文件，如果为None则保留所有文件

        返回:
            解压后的目录路径
        """
        # 检查文件是否存在
        archive_path = Path(archive_path)
        if not archive_path.exists():
            raise FileNotFoundError(f"压缩文件不存在: {archive_path}")

        # 处理扩展名参数
        ext_set = None
        if extensions is not None and len(extensions) > 0:
            # 确保扩展名以点开头并转换为小写
            ext_set = set()
            for ext in extensions:
                if not ext.startswith('.'):
                    ext = '.' + ext
                ext_set.add(ext.lower())

        # 创建输出目录
        output_dir = self._create_output_dir(output_path)
        logger.info(f"解压到目录: {output_dir}")

        try:
            # 先解压文件（包括递归解压嵌套压缩包）
            self._extract_file(archive_path, output_dir, password, recursive)

            # 如果需要展平，在所有解压完成后进行
            if flatten:
                self._flatten_directory(output_dir)

            # 最后，根据扩展名过滤文件（只有在明确指定扩展名时才过滤）
            if ext_set:
                self._filter_files_by_extension(output_dir, ext_set)

        except Exception as e:
            # 清理输出目录（如果是临时目录）
            if output_path is None and os.path.exists(output_dir):
                shutil.rmtree(output_dir, ignore_errors=True)
                # 从跟踪列表中移除
                if output_dir in self._temp_dirs:
                    self._temp_dirs.remove(output_dir)
            raise e

        return output_dir


# 使用示例
if __name__ == "__main__":
    pass
    # 方式1：使用上下文管理器（推荐，自动清理临时目录）
    # with UniversalExtractor() as extractor:
    #     result_path = extractor.extract("archive.zip")
    #     # 使用 result_path...
    # # 退出 with 块后自动清理临时目录

    # 方式2：传统方式
    # extractor = UniversalExtractor()

    # 带密码解压
    # result_path = extractor.extract("encrypted.zip", password="secret")

    # 指定输出路径并扁平化
    # result_path = extractor.extract("archive.rar", output_path="/tmp/output", flatten=True)

    # 只提取特定扩展名的文件
    # result_path = extractor.extract("archive.zip", extensions=[".txt", ".jpg"])
    # result_path = extractor.extract("archive.zip", extensions=["txt", "jpg"])  # 也可以不带点

    # 基本用法
    # result_path = extractor.extract(file_path, output_path=os.path.join("output", file_name))

    # 手动清理临时目录（如果不使用上下文管理器）
    # extractor.cleanup()
