from typing import List

class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        # 1. Подсчитываем частоту каждого числа
        freq_map = {}
        for num in nums:
            freq_map[num] = freq_map.get(num, 0) + 1
        
        # 2. Создаем корзины (buckets)
        # Индекс корзины = частота, значение = список чисел с этой частотой
        buckets = [[] for _ in range(len(nums) + 1)]
        
        # 3. Распределяем числа по корзинам в зависимости от их частоты
        for num, count in freq_map.items():
            buckets[count].append(num)
        
        # 4. Собираем k самых частых элементов
        result = []
        # Идем от самых высоких частот к самым низким
        for i in range(len(buckets) - 1, 0, -1):
            if buckets[i]:  # если корзина не пустая
                for num in buckets[i]:
                    result.append(num)
                    if len(result) == k:
                        return result
        
        return result

# Тестирование
s = Solution()
print(s.topKFrequent([1,1,1,2,2,3], k=2))  # Output: [1,2]
print(s.topKFrequent([1], k=1))            # Output: [1]
print(s.topKFrequent([1,2,1,2,1,2,3,1,3,2], k=2))  # Output: [1,2]