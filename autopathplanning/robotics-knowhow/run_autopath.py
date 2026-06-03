import sys
sys.path.append('d:/robotics-knowhow')

from autopath.search import SearchPolicy
from autopath.scenarios import get_default_scenarios

def main():
    print("=" * 60)
    print("AutoPath 自进化路径规划演示")
    print("=" * 60)
    
    scenarios = get_default_scenarios()
    print(f"加载 {len(scenarios)} 个测试场景")
    for i, s in enumerate(scenarios):
        print(f"  场景 {i+1}: {s['name']}")
    
    print("\n启动遗传算法搜索...")
    searcher = SearchPolicy(scenarios)
    
    try:
        best_params, best_score = searcher.genetic_search(generations=5, pop_size=5)
        
        print("\n" + "=" * 60)
        print("搜索完成!")
        print(f"最佳得分: {best_score:.2f}")
        print("\n最佳参数:")
        for key, value in best_params.items():
            print(f"  {key}: {value:.4f}")
        
        searcher.save_results('results.tsv')
        searcher.save_best_params('best_params.json')
        print("\n结果已保存到 results.tsv 和 best_params.json")
        
    except Exception as e:
        print(f"搜索过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()