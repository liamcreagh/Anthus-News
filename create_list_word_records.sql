drop table if exists list_wf_rec;

CREATE TABLE list_wf_rec
(
  frequency integer,
  list_id bigint NOT NULL,
  word_id integer NOT NULL,
  CONSTRAINT list_wf_rec_pkey PRIMARY KEY (list_id, word_id),
  CONSTRAINT list_wf_rec_fkey FOREIGN KEY (list_id)
      REFERENCES list_rec (list_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE list_wf_rec
  OWNER TO nlstudent;
  
CREATE INDEX fki_list_wf_rec_fkey2
  ON list_wf_rec
  USING btree
  (word_id);


drop table if exists list_word_rec;
CREATE TABLE list_word_rec
(
  word_id serial NOT NULL,
  word text,
  CONSTRAINT list_word_rec_pkey PRIMARY KEY (word_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE list_word_rec
  OWNER TO nlstudent;



