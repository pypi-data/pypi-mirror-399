
"""
文本特征提取
"""
import sys,os 
import pandas as pd
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

from tpf.conf import pc  
from tpf.d1 import DataDeal as dtl
from tpf.d1 import read,write 
from tpf.mlib.modelbase import MLBase 
from tpf.mlib import ModelEval as me 
from tpf.nlp.text import BM25Reranker
from tpf.nlp.bgm import Reranker



class TextClassifier:
    def __init__(self,
                 data_path,
                 model_path_rerank,
                 model_path_ms,
                 data_train_csv,
                 data_test_csv,
                 label_name,
                 use_cols,
                 model_save_dir,
                 global_log_path,
                 feature_sim_top_k,
                 feature_label_top_k,
                 out_dir):
        """文本分类
        """
        self.data_path  = data_path
        self.model_path_rerank = model_path_rerank  
        self.model_path_ms  = model_path_ms
        self.data_train_csv = data_train_csv
        self.data_test_csv  = data_test_csv
        self.data_split()
        self.label_name = label_name
        self.feature_sim_top_k   = feature_sim_top_k
        self.feature_label_top_k = feature_label_top_k
        self.out_dir = out_dir 
        
        self.use_cols  = use_cols
        self.model_v   = 1
        self.model2    = None 
        self.model3    = None 
        self.ms = None
        self.reranker  = None
        
        self.ml = MLBase(
            model_save_dir = model_save_dir,
            log_path       =global_log_path)
        
    def set_model_version(self, model_v=2):
        self.model_v = model_v 
        

    def data_split(self,test_size=0.2):
        """
        数据集切分，确保每个标签拆分出一定的数据
        - 输出:保存测试集到data_test_csv
        
        """
        df = pd.read_csv(self.data_path)
        train,test = dtl.data_split(df, df[self.label_name], test_size=test_size)
        self.train = train 
        self.test = test
        test.to_csv(self.data_test_csv, index=False) #测试集保存的是原始文本
        
        
    def _bm25_fit(self,df =None, use_cols=['text', 'label']):
        if df is None:
            df = self.train
        self.bm25 = BM25Reranker(df, use_cols=use_cols)
 
    def bm25_cross_scores(self, df=None, use_cols=['text', 'label']):
        """对训练集生成BM25排序数据
        - 第i条数据与剩下的n-1条数据进行BM25排序，生成训练集
        
        """
        if df is None:
            df = self.train
        bm25 = BM25Reranker(df, use_cols=use_cols)
        df = bm25.epoch_cross_scores(sim_top_k=self.feature_sim_top_k, label_top_k=self.feature_label_top_k, save_path = self.out_dir)
        return df
         
        
    def bm25_predict(self, df=None):
        """
        - df需要有两个列use_cols=['text', 'label']，一个文本列，一个标签列
        - 其中label列在预测的时候可以没有
        
        """
        sim_top_k  =self.feature_sim_top_k
        label_top_k=self.feature_label_top_k
        
        if df is None:
            df = self.test
        df_topk = self.bm25.data_topk_batch(df, sim_top_k=sim_top_k, label_top_k=label_top_k,outdir=self.out_dir)
        return df_topk

    def _rerank_fit(self):
        if self.reranker is None:
            self.reranker = Reranker(model_name=self.model_path_rerank)
        
    def rerank_predict(self, df, use_cols=['query_text','sim_text'], batch_size=100):
        # 进行重排序
        df['reranked_score'] = self.reranker.rerank_score(df, use_cols=use_cols, batch_size=batch_size)
        return df 
    
    def _ms_fit(self):
        """加载MS模型
        """
        self.ms = Reranker(model_name=self.model_path_ms)
        
    def ms_predict(self, df, use_cols=['query_text','sim_text'], batch_size=100):
        # 进行重排序
        df['ms_score'] = self.ms.rerank_score(df, use_cols=use_cols, batch_size=batch_size)
        return df 
    
    
    def data_feature_add(self, df, model_v=2):
        print(f"数据特征添加，模型版本: {model_v}")
        if model_v == 2:
            df =  self.data_feature_add2(df)
        elif model_v == 3:
            print("数据特征添加，模型版本: 3....")
            df['mean_reranked_score'] = df.groupby('sim_label')['reranked_score'].transform('mean')
            df['mean_ms_score']       = df.groupby('sim_label')['ms_score'].transform('mean')
            df['std_reranked_score']  = df.groupby('sim_label')['reranked_score'].transform('std')
            df['std_ms_score']        = df.groupby('sim_label')['ms_score'].transform('std')
            df['zscore_reranked_score'] = (df['reranked_score'] - df['mean_reranked_score']) / df['std_reranked_score']
            df['zscore_ms_score'] = (df['ms_score'] - df['mean_ms_score']) / df['std_ms_score']
            # df['mean_bm25_sim_score'] = df.groupby('sim_label')['bm25_sim_score'].transform('mean')
            df['std_bm25_sim_score'] = df.groupby('sim_label')['bm25_sim_score'].transform('std')
            df['zscore_bm25_sim_score'] = (df['bm25_sim_score'] - df['bm25_mean_score']) / df['std_bm25_sim_score']
            self.use_cols.extend(['mean_reranked_score','mean_ms_score','std_reranked_score','std_ms_score','zscore_reranked_score','zscore_ms_score','std_bm25_sim_score','zscore_bm25_sim_score'])
        return df
        
    def feature_names(self):
        use_cols = set(self.use_cols)
        use_cols = sorted(use_cols)
        self.use_cols = use_cols
        return use_cols
    
    def data_feature_add2(self,df):
        df['mean_reranked_score'] = df.groupby('sim_label')['reranked_score'].transform('mean')
        df['mean_ms_score']       = df.groupby('sim_label')['ms_score'].transform('mean')
        self.use_cols.extend(['mean_reranked_score','mean_ms_score'])
        return df
    
    
    def corr_fit(self,use_cols=['text', 'label']):
        import time
        #step1:以self.train为基础数据，初始化bm25排序算法
        step1_start = time.time()
        self._bm25_fit(df=self.train,use_cols=use_cols)
        step1_time = time.time() - step1_start

        #step2: 新增rerank排序
        step2_start = time.time()
        self._rerank_fit()  #加载模型
        step2_time = time.time() - step2_start
        
        #step3: 新增MS排序
        step3_start = time.time()
        self._ms_fit()      #加载模型
        step3_time = time.time() - step3_start
        
        print("======================")
        print(f"[data_feature_gen] step1(BM25排序): {step1_time:.3f}s, step2(Rerank排序): {step2_time:.3f}s, step3(MS排序): {step3_time:.3f}s, 总计: {step1_time+step2_time+step3_time:.3f}s")
        print("======================") 
    
    
    def corr_transform(self, df, model_v=2):
        pass 
    
    def feature_with_train_datasets(self, df, is_train=True, model_v=2,label_name='match'):
        """
        以df为query，以训练集为模板，进行BM25、Rerank、MS排序，生成预测分数数据
        - 每个query对应三个标签，使用model对这三个标签打分，分数高者为预测结果
        - 预测数据集中没有real_label列，这是需要预测的；其他列与训练集相同
        """
        import time

        #step1:以self.train为基础数据，初始化bm25排序算法
        step1_start = time.time()
        # self._bm25_fit(df=self.train, use_cols=['text', 'label'])
        # 以df与train数据生成bm25排序
        df_bm25 = self.bm25_predict(df=df, sim_top_k=self.feature_sim_top_k, label_top_k=self.feature_label_top_k)  #返回sim_top_k*label_top_k条数据
        df_bm25 = df_bm25.rename(columns={'sim_score': 'bm25_sim_score','mean_score': 'bm25_mean_score'})
        step1_time = time.time() - step1_start

        #step2: 新增rerank排序
        step2_start = time.time()
        # self._rerank_fit()  #加载模型
        df_rank = self.rerank_predict(df_bm25,use_cols=['query_text','sim_text'], batch_size=100) #实时计算两个列的相关性
        step2_time = time.time() - step2_start

        #step3: 新增MS排序
        step3_start = time.time()
        # self._ms_fit()      #加载模型
        df = self.ms_predict(df_rank, use_cols=['query_text','sim_text'], batch_size = 100)
        msg = f"is_train:{is_train},model_v:{model_v}"
        print(msg)
        df = self.data_feature_add(df,model_v=model_v)
        step3_time = time.time() - step3_start
        print("======================")
        print(f"[data_feature_gen] step1(BM25排序): {step1_time:.3f}s, step2(Rerank排序): {step2_time:.3f}s, step3(MS排序): {step3_time:.3f}s, 总计: {step1_time+step2_time+step3_time:.3f}s")
        print("======================")

        pc.lg(f"数据生成完成，数据维度: {df.shape}")
        pc.lg(f"df.columns: {df.columns.tolist()}")
        if is_train:
            df[label_name] = (df['sim_label'] == df['real_label']).astype(int)
            df.to_csv(self.data_train_csv, index=False)
            pc.lg(f"数据保存到{self.data_train_csv}")
        return df
    
    def feature_train_datasets_only(self, model_v=2, label_name='match'):
        """
        以训练集为query，进行BM25、Rerank、MS排序，生成训练集
        - 取第i条数据与剩下的n-1条数据进行BM25排序，生成训练集
        - 输入: target_data_file2k80%的数据，为训练集的原始数据
        - 输出: 数据保存到data_train_csv
        """
        # self._bm25_fit()
        df_bm25 = self.bm25_cross_scores(df=self.train)
        df_bm25 = df_bm25.rename(columns={'sim_score': 'bm25_sim_score','mean_score': 'bm25_mean_score'})
        
        # self._rerank_fit()
        df_rank = self.rerank_predict(df_bm25, use_cols=['query_text', 'sim_text'],batch_size=100)
        
        # self._ms_fit()
        df = self.ms_predict(df_rank) 
        df[label_name] = (df['sim_label'] == df['real_label']).astype(int)

        df = self.data_feature_add(df,model_v=model_v)
        
        pc.lg(f"数据生成完成，数据维度: {df.shape}")
        pc.lg(f"df.columns: {df.columns.tolist()}")
        df.to_csv(self.data_train_csv, index=False)
        pc.lg(f"数据保存到{self.data_train_csv}")
        return df


    def lr_fit(self, df=None, 
               use_cols=None,
               label_name='match',model_v=2):
        """
        训练Logistic回归分类模型，保存至model_path_lr；从data_train_csv读取数据，然后拆分，训练，评估
        - 输入: data_train_csv的数据，由target_data_file2的80%计算得分而来
        - 输出: 
          - 训练好的逻辑回归模型，保存至model_path_lr
          - config.model_eval_path,以dict格式记录acc,recall,precision

        Returns:
            LogisticRegression: 训练好的逻辑回归模型

        功能说明:
            1. 数据加载与切分：将数据按8:2比例切分为训练集和测试集
            2. 特征准备：分离特征矩阵X和标签向量y
            3. 模型训练：使用LogisticRegression进行二分类训练
            4. 模型评估：计算准确率、召回率、精确率等指标
            5. 模型保存：将训练好的模型存储在self.lr_model中供后续使用

        评估指标:
            - 准确率(accuracy): 预测正确的样本比例
            - 召回率(recall): 真实正例中被正确预测的比例
            - 精确率(precision): 预测为正例中真实为正例的比例
        """
        data_path=self.data_train_csv,
        if df is None:
            df = pd.read_csv(data_path)
        if use_cols is None:
            use_cols = self.feature_names()
            
        print("use_cols",use_cols)
        
        # 训练预测
        if label_name in use_cols:
            feature_cols = [col for col in use_cols if col not in [label_name]]
        else:
            feature_cols = use_cols.copy()
            use_cols.append('match')

        data= df[use_cols]
        self.ml.set_model_msg(model_type='lr', 
                              model_version=model_v, 
                              feature_cols=feature_cols,
                              model_params={"max_iter":10000})
        
        X_train, X_test, y_train, y_test = self.ml.data_split(data, label_name=label_name, test_size=0.2, random_state=42,is_returnXy=True)

        model = self.ml.fit(X_train, y_train)
        self.ml.model_save()
        score  = self.ml.score(X_test, y_test)  #精确率
        y_pred = self.ml.predict(X_test)  # 计算召回率和精确率
        recall = self.ml.recall_score(y_test, y_pred)

        # 计算预测为1的数据中真实为1的比例（精确率）
        precision = self.ml.precision_score(y_test, y_pred)
        fenmu = (y_pred==1).sum()
        fenzi = y_pred[(y_pred==1) & (y_test==1)].sum()

        pc.lg(f"模型训练完成，准确率: {round(score,4)}")
        pc.lg(f"模型召回率: {round(recall,4)}")
        pc.lg(f"预测为1的数据中真实为1的比例（精确率）: {round(precision,4)},{fenzi}/{fenmu}={round(fenzi/fenmu,4)}")
        
        return model 
    
    
    def lr_valid(self, model, df=None, label_name='match', model_v=2):
        """验证集预测 
        - df为原始的text,label
        """
        if df is None:
            df = self.test
        
        df_valid = self.feature_with_train_datasets(df, model_v=model_v)
        print(df_valid.columns.tolist())
        if label_name not in df_valid.columns.tolist():
            raise Exception(f"{label_name}列不存在")
        y_test = df_valid[label_name]
        use_cols = self.feature_names()
        df_valid = df_valid[use_cols]
        print(df_valid.columns.tolist())
        if label_name in df_valid.columns.tolist():
            df = df_valid.drop(columns=[label_name])
        else:
            df = df_valid
    
        print(df.columns.tolist())
        y_pred = model.predict(X=df)
        acc_p = me.acc_lr(y_label=y_test, y_pred=y_pred)
        
        return acc_p
    
    def predict(self,texts=[],use_cols=None, is_save_file=True,model_v=2,label_name='match'):
        """
        - 输入:模型，原始文本
        - 输出：
            - 中间结果保存至data_predict_3label，一个text对应三个可能标签
            - 预测结果：一个text对应一个标签与一个分数概率
        """
        import time

        if use_cols is None:
            use_cols = self.use_cols
        if label_name in use_cols:
            use_cols.remove(label_name)

        #step1: 特征生成
        step1_start = time.time()
        df = pd.DataFrame({'text':texts})
        df_feature = self.feature_with_train_datasets(df, is_train=False,model_v=model_v)
        print(df_feature.columns.tolist())
        # print(use_cols)
        # use_cols = self.feature_names()
        # X = df_feature[use_cols]
        step1_time = time.time() - step1_start
        
        #step2: 模型预测
        step2_start = time.time()
        y_pred = self.ml.predict_proba(X=df_feature, model_type='lr', model_version=model_v)
        step2_time = time.time() - step2_start

        #step3: 模型结果保存
        step3_start = time.time()
        y_prob = y_pred[:,1]
        if model_v == 2:
            df_feature['prob'] = 1-y_prob  #df['sim_label'] == df['real_label']
        elif model_v == 3:
            df_feature['prob'] = y_prob
        else:
            df_feature['prob'] = y_prob
        df_final = df_feature[['query_text','sim_label','prob']]
        if is_save_file:
            df_final.to_csv(config.data_predict_3label, index=False)
        df_3label = df_final.copy()
        df_3label['prob_mean'] = df_3label.groupby('sim_label')['prob'].transform('mean')
        df_3label = df_3label.sort_values('prob_mean', ascending=False)

        df_final = df_3label.loc[df_3label.groupby('query_text')['prob'].idxmax()]
        # df_final = df_3label.loc[df_3label.groupby('query_text')['prob_mean'].idxmax()]
        step3_time = time.time() - step3_start

        print(f"[predict] step1(特征生成): {step1_time:.3f}s, step2(模型预测): {step2_time:.3f}s, step3(结果保存): {step3_time:.3f}s, 总计: {step1_time+step2_time+step3_time:.3f}s")

        return df_final,df_3label

    def model_save(self, model_path):
        """
        保存训练好的LR模型
        Args:
            model_path (str): 模型保存路径
        """
        if not hasattr(self, 'lr_model'):
            raise Exception("未找到训练的LR模型，请先调用lr_fit方法训练模型")

        import joblib
        joblib.dump(self.lr_model, model_path)
        pc.lg(f"LR模型已保存到: {model_path}")

    def model_load(self, model_path):
        """
        加载训练好的LR模型
        Args:
            model_path (str): 模型文件路径
        Returns:
            LogisticRegression: 加载的LR模型
        """
        import joblib
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")

        self.lr_model = joblib.load(model_path)
        pc.lg(f"LR模型已从 {model_path} 加载")
        return self.lr_model 



