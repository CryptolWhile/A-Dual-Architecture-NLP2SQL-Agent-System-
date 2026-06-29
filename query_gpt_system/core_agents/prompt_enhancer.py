from agno.agent import Agent
from agno.models.openai import OpenAIChat

def get_prompt_enhancer_agent() -> Agent:
    """
    Agent này có nhiệm vụ nhận câu hỏi thô của user, 
    diễn giải và mở rộng thành một câu hỏi chi tiết, rõ ràng hơn
    giúp các agent phía sau dễ dàng xác định ngữ cảnh và intent.
    """
    return Agent(
        name="Prompt Enhancer",
        role="Mở rộng và làm rõ ý định của câu hỏi người dùng",
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=[
            "Bạn nhận được một câu hỏi ngắn gọn hoặc có phần mơ hồ từ người dùng muốn tra cứu dữ liệu (trong hệ thống Query GPT).",
            "Nhiệm vụ của bạn là diễn giải lại và mở rộng câu hỏi này thành một câu hỏi chi tiết, rõ ràng hơn.",
            "Ví dụ: 'average fare' -> 'Tính giá trị trung bình (average) của cột fare trong bảng dữ liệu liên quan đến vận tải/hành khách'.",
            "Mục tiêu là giúp hệ thống dễ dàng nhận diện chủ đề, bảng (table), và cột dữ liệu (column) hơn.",
            "Chỉ trả về câu hỏi đã được mở rộng. KHÔNG trả lời hay giải thích thêm."
        ]
    )

def enhance_query(query: str) -> str:
    """
    Hàm tiện ích nhận câu hỏi người dùng và trả về câu hỏi đã được mở rộng.
    """
    agent = get_prompt_enhancer_agent()
    response = agent.run(query)
    return response.content.strip()

if __name__ == "__main__":
    # Test nhanh
    test_query = "average fare"
    print("Câu hỏi gốc:", test_query)
    print("Câu hỏi mở rộng:", enhance_query(test_query))
