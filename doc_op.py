"""
    拆分文档，按照二级标题（\n\n## ）把 md 文件拆分为一段一段
"""

import os


def split_doc(file_path):
    """
        拆分一个文档的内容
    :param file_path: 文档路径
    :return: 拆分后的文档的片段 - [chunk1, chunk2, ...]
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # 按照二级标题（\n\n  ## ）把 md 文件拆分为一段一段
    chunk_list = content.split("\n\n## ")

    return chunk_list


def split_docs(file_dir):
    """
        拆分一个目录中的全部文档
    :param file_dir: 文档目录
    :return: 拆分后的文档的片段信息 - [{"doc_name": "", "doc_chunk": ""}, {}, ...]
    """
    doc_name_chunk_list = []
    for file_name in os.listdir(file_dir):
        file_path = os.path.join(file_dir, file_name)

        single_doc_chunk_list = split_doc(file_path)
        for single_doc_chunk in single_doc_chunk_list:
            chunk_info = {
                "doc_name": file_name,
                "doc_chunk": single_doc_chunk
            }

            doc_name_chunk_list.append(chunk_info)

    return doc_name_chunk_list


if __name__ == '__main__':
    # test_file_path = "./documents/vllm 的安装和使用.md"
    # ret = split_doc(test_file_path)
    # print(ret[2])

    test_file_dir = "./documents"
    ret2 = split_docs(test_file_dir)
    for i, doc_chunk_info in enumerate(ret2):
        print(doc_chunk_info)
        if i >= 4:
            break
