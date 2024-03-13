import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from streamlit_extras.add_vertical_space import add_vertical_space
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback

# Sidebar contents
with st.sidebar:
    st.title('🤗💬 LLM Chat App')
    st.markdown('''
    ## About
    This app is an LLM-powered chatbot built using:
    - [Streamlit](https://streamlit.io/)
    - [LangChain](https://python.langchain.com/)
    - [OpenAI](https://platform.openai.com/docs/models) LLM model

    ''')
    add_vertical_space(5)
    st.write('Made by WinEisEis')

load_dotenv()


def main():
    st.header("Chat with pdf")

    # upload a pdf file
    pdf = st.file_uploader("Upload your PDF", type='pdf')

    # st.write(pdf)
    if pdf is not None:
        # pdf reader
        pdf_reader = PdfReader(pdf)

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text=text)

        # Convert the chunks of text into embeddings to form the knowledge base
        embeddings = OpenAIEmbeddings()
        knowledgeBase = FAISS.from_texts(chunks, embeddings)

        # Accept user questions/query
        query = st.text_input("Ask questions about your PDF file:")
        st.write(query)

        if query:
            docs = knowledgeBase.similarity_search(query=query, k=3)

            llm = OpenAI(model_name="gpt-4-0125-preview",
                         temperature=0)
            with st.spinner("Processing..."):
                chain = load_qa_chain(llm=llm, chain_type="stuff")

                with get_openai_callback() as cost:
                    response = chain.run(input_documents=docs, question=query)
                    print(cost)
                st.write(response)


if __name__ == '__main__':
    main()
