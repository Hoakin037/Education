def counting_sort(alist, largest):
    c = [0]*(largest + 1)
    for i in range(len(alist)):
        c[alist[i]] = c[alist[i]] + 1 # equal c[alist[i]] += 1 
 
    result = []
    result = [i for i in range(len(c)) for _ in range(c[i])] # Ускоренная версия
    
    return result

class Solution:
    def minimumAbsDifference(self, arr: List[int]) -> List[List[int]]:
        if len(arr) <= 2:
            return [arr]
        abs_min = max(arr)
        arr = sorted(arr)
        lst_difs = [[]]
        for i in range(len(arr) - 1):
            current_diff = arr[i + 1] - arr[i]
        
            if current_diff < abs_min:
                abs_min = current_diff
                lst_difs = [[arr[i], arr[i + 1]]]  
            elif current_diff == abs_min:
                lst_difs.append([arr[i], arr[i + 1]])
    

        return lst_difs



