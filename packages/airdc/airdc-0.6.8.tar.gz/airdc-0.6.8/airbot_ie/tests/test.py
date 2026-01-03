from pydantic import BaseModel, ConfigDict, model_validator
from typing import List


class Base(BaseModel):
    names: List[str] = []
    processed: List[str] = []

    @model_validator(mode="after")
    def parent_validator(self):
        print(
            f"\n[Parent Validator] Executing. Current processed len: {len(self.processed)}"
        )
        # 模拟填充逻辑
        if not self.processed and self.names:
            # 绕过 frozen 限制的操作方式
            object.__setattr__(self, "processed", ["done"] * len(self.names))
        return self


class FrozenChild(Base, frozen=True):
    @model_validator(mode="after")
    def child_validator(self):
        print(
            f"\n[Child Validator] Executing. Current processed len: {len(self.processed)}"
        )
        return self

    def model_post_init(self, __context):
        print(f"[Child Post-Init] Executing. Processed len: {len(self.processed)}")
        # 这里会尝试访问由父类填充的字段
        if len(self.processed) == 0:
            print("[Child Post-Init] Error: Processed is empty!")
        print(self.processed)


class NormalChild(Base):
    def model_post_init(self, __context):
        print(f"[Child Post-Init] Executing. Processed len: {len(self.processed)}")
        # 这里会尝试访问由父类填充的字段
        if len(self.processed) == 0:
            print("[Child Post-Init] Error: Processed is empty!")
        print(self.processed)

    @model_validator(mode="after")
    def child_validator(self):
        print(
            f"\n[Child Validator] Executing. Current processed len: {len(self.processed)}"
        )
        return self



# --- 测试用例 ---


def test_frozen_vs_normal_behavior():
    print("\n" + "=" * 30)
    print("TESTING NORMAL CHILD (frozen=False)")
    print("=" * 30)
    n = NormalChild(names=["a", "b"])

    print("\n" + "=" * 30)
    print("TESTING FROZEN CHILD (frozen=True)")
    print("=" * 30)
    f = FrozenChild(names=["a", "b"])


if __name__ == "__main__":
    test_frozen_vs_normal_behavior()
