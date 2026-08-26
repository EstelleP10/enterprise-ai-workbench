def split_text(text, chunk_size=150):
    chunks = []

    current_chunk = ""

    paragraphs = text.split("\n")

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        if len(current_chunk) + len(paragraph) <= chunk_size:
            current_chunk += paragraph + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


text = """差旅报销管理制度
第一条 员工因公出差产生的交通费、住宿费及符合规定的市内交通费用可以申请报销。
第二条 市内打车费用原则上应提供有效发票及行程记录。
第三条 员工住宿费用按照公司规定的城市及职级标准执行。
第四条 出差期间产生的餐费按照公司差旅补贴标准执行。"""


chunks = split_text(text)

for i, chunk in enumerate(chunks, start=1):
    print(f"--- Chunk {i} ---")
    print(chunk)
    print()